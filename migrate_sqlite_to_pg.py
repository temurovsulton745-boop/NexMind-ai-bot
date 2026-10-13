"""
Eski users.db (SQLite) dagi foydalanuvchilarni PostgreSQL'ga ko'chiradi.

Ishlatish (kompyuteringizda, bir marta):
    pip install psycopg2-binary
    set DATABASE_URL=postgresql://...        (Windows)
    export DATABASE_URL=postgresql://...     (Mac/Linux)
    python migrate_sqlite_to_pg.py users.db

Avval botni PostgreSQL bilan kamida bir marta ishga tushiring (jadvallar yaratilishi uchun).
Skript xavfsiz: mavjud foydalanuvchilarni qayta yozmaydi.
"""
import os
import sqlite3
import sys

import psycopg2

sqlite_path = sys.argv[1] if len(sys.argv) > 1 else "users.db"
dsn = os.getenv("DATABASE_URL")
if not dsn:
    sys.exit("DATABASE_URL o'rnatilmagan")

src = sqlite3.connect(sqlite_path)
src.row_factory = sqlite3.Row
dst = psycopg2.connect(dsn)
cur = dst.cursor()

cols = [r[1] for r in src.execute("PRAGMA table_info(users)").fetchall()]
rows = src.execute("SELECT * FROM users").fetchall()
placeholders = ", ".join(["%s"] * len(cols))
sql = (
    f"INSERT INTO users ({', '.join(cols)}) VALUES ({placeholders}) "
    "ON CONFLICT (user_id) DO NOTHING"
)
for row in rows:
    cur.execute(sql, tuple(row[c] for c in cols))
print(f"users: {len(rows)} ta qator ko'rib chiqildi")

hist = src.execute(
    "SELECT user_id, role, content FROM history ORDER BY rowid"
).fetchall()
for r in hist:
    cur.execute(
        "INSERT INTO history (user_id, role, content) VALUES (%s, %s, %s)",
        (r["user_id"], r["role"], r["content"]),
    )
print(f"history: {len(hist)} ta qator ko'chirildi")

dst.commit()
dst.close()
print("Tayyor ✅")
