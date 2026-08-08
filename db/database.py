import aiosqlite


class Database:
    def __init__(self, path: str):
        self.path = path

    async def connect(self):
        self.db = await aiosqlite.connect(self.path)

        await self.db.execute("PRAGMA journal_mode=WAL")
        await self.db.execute("PRAGMA busy_timeout=5000")
        await self.db.execute("PRAGMA foreign_keys=ON")

        await self.db.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY
            );

            CREATE TABLE IF NOT EXISTS cars (
                number TEXT PRIMARY KEY
            );

            CREATE TABLE IF NOT EXISTS users_to_cars (
                owner TEXT REFERENCES users(id) ON DELETE CASCADE,
                number TEXT REFERENCES cars(number) ON DELETE CASCADE,
                PRIMARY KEY (owner, number)
            );

            CREATE INDEX IF NOT EXISTS idx_users_to_cars_owner ON users_to_cars(owner);
            CREATE INDEX IF NOT EXISTS idx_users_to_cars_number ON users_to_cars(number);

            CREATE TABLE IF NOT EXISTS licenses (
                license_number TEXT,
                reg_number TEXT REFERENCES cars(number) ON DELETE CASCADE,
                start_date TEXT,
                end_date TEXT,
                allowed_zona TEXT,
                type TEXT,
                license_type TEXT,
                status TEXT,
                cancellation_date TEXT,
                PRIMARY KEY (reg_number, license_number)
            );

            CREATE INDEX IF NOT EXISTS idx_licenses_reg_number ON licenses(reg_number);
        ''')

        await self.db.commit()

    async def close(self):
        await self.db.close()
