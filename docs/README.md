# Week 8 — Database Lab (CST1510)

## Quick start

1. Create virtual env: `python -m venv .venv`
2. Activate env and `pip install -r requirements.txt`
3. Place CSVs in `DATA/` if you want them imported.
4. Run `python main.py` to create DB and run demo.

## Notes

- All DB writes use parameterised queries to avoid SQL injection.
- Passwords stored as bcrypt hashes.
- Use DB Browser for SQLite to view `DATA/intelligence_platform.db`.
