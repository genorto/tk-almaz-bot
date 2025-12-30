python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

cat > .env << EOF
BOT_TOKEN=""
PASSWORD=""
API_KEY=""
EOF

mkdir resources/
touch resources/users.json
touch resources/plates.json
