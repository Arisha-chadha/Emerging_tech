# ClassConnect Flask Backend (Quick Start)

## 1) Setup
```bash
python -m venv .venv
# Windows: py -m venv .venv
source .venv/bin/activate
# Windows: .\.venv\Scripts\Activate
pip install -r requirements.txt
cp .env.example .env
```

Make sure your frontend runs on http://127.0.0.1:5500 (VS Code Live Server).
If using a different port, add it to CORS_ORIGINS in `.env`.

## 2) Initialize DB
```bash
flask --app run.py db init
flask --app run.py db migrate -m "init"
flask --app run.py db upgrade
```

## 3) Run
```bash
python run.py
```

## 4) Create test users
Use Postman or curl to call `POST /api/auth/register` for a professor & student.
Then login via `POST /api/auth/login` to get a token for protected endpoints.
