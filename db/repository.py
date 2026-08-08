from config import db


async def add_user(id: str) -> None:
    await db.db.execute('''
        INSERT OR IGNORE INTO users (id)
        VALUES (?)
    ''', (id,))

    await db.db.commit()

async def remove_user(id: str) -> None:
    await db.db.execute('''
        DELETE FROM users
        WHERE id = ?
    ''', (id,))

    await db.db.commit()

async def add_plate_to_user(user_id: str, number: str) -> None:
    await db.db.execute('''
        INSERT OR IGNORE INTO cars (number)
        VALUES (?)
    ''', (number,))

    await db.db.execute('''
        INSERT OR IGNORE INTO users_to_cars (owner, number)
        VALUES (?, ?)
    ''', (user_id, number))

    await db.db.commit()

async def delete_plate_from_user(user_id: str, number: str) -> None:
    await db.db.execute('''
        DELETE FROM users_to_cars
        WHERE owner = ? AND number = ?
    ''', (user_id, number))

    async with db.db.execute('''
        SELECT 1 FROM users_to_cars WHERE number = ? LIMIT 1
    ''', (number,)) as cursor:
        still_tracked = await cursor.fetchone()

    if not still_tracked:
        await db.db.execute('''
            DELETE FROM cars WHERE number = ?
        ''', (number,))

    await db.db.commit()

async def get_user_plates(user_id: str) -> list:
    async with db.db.execute('''
        SELECT number FROM users_to_cars WHERE owner = ?
    ''', (user_id,)) as cursor:
        rows = await cursor.fetchall()
        return [{"plate": row[0]} for row in rows]

async def get_licenses_for_car(number: str) -> list:
    async with db.db.execute('''
        SELECT * FROM licenses WHERE reg_number = ?
    ''', (number,)) as cursor:
        headers = [metadata[0] for metadata in cursor.description]
        rows = await cursor.fetchall()
        return [dict(zip(headers, row)) for row in rows]

async def update_car_licenses(number: str, licenses: list) -> None:
    await db.db.execute('''
        INSERT OR IGNORE INTO cars (number)
        VALUES (?)
    ''', (number,))

    await db.db.execute('''
        DELETE FROM licenses
        WHERE reg_number = ?
    ''', (number,))

    values = []
    for license in licenses:
        values.append((
            license["licenseNumber"],
            license["regNumber"],
            license["startDate"],
            license["endDate"],
            license["allowedZona"],
            license["type"],
            license["licenseType"],
            license["status"],
            license["cancellationDate"],
        ))

    await db.db.executemany('''
        INSERT INTO licenses (license_number,
                              reg_number,
                              start_date,
                              end_date,
                              allowed_zona,
                              type,
                              license_type,
                              status,
                              cancellation_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', values)

    await db.db.commit()

async def get_tracked_plates() -> list:
    async with db.db.execute('''
        SELECT owner, number FROM users_to_cars
    ''') as cursor:
        rows = await cursor.fetchall()
        return [{"owner": row[0], "number": row[1]} for row in rows]
