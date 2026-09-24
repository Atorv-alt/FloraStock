"""Тесты auth-схемы: хеш паролей и SQL-миграция 08 (контракт с backend)."""

import base64
import hashlib
from pathlib import Path


def csharp_hash(password: str) -> str:
    """Повтор схемы Core.Services.PasswordHasher: Base64(SHA256(password + 'salt'))."""
    digest = hashlib.sha256((password + "salt").encode("utf-8")).digest()
    return base64.b64encode(digest).decode()


def test_hash_format_matches_backend_scheme():
    h = csharp_hash("admin")
    assert len(h) == 44
    assert h.endswith("=")
    # детерминированность схемы
    assert csharp_hash("admin") == h
    assert csharp_hash("admin") != csharp_hash("admin1")


def test_seed_passwords_differ_from_plaintext():
    assert csharp_hash("admin") != "admin"
    assert csharp_hash("ivanova123") != "ivanova123"


def test_08_sql_is_idempotent_and_complete():
    sql = (Path(__file__).parent.parent / "docs" / "sql" / "08_auth_login.sql").read_text(encoding="utf-8")
    assert "ADD COLUMN IF NOT EXISTS login" in sql
    assert "CREATE UNIQUE INDEX IF NOT EXISTS uq_employee_login" in sql
    # backfill логина и разрешение коллизий
    assert "split_part(email" in sql
    assert "lower(x.login) = lower(e.login)" in sql


def test_09_sql_is_idempotent_and_complete():
    sql = (Path(__file__).parent.parent / "docs" / "sql" / "09_client_is_active.sql").read_text(encoding="utf-8")
    assert "ADD COLUMN IF NOT EXISTS isactive" in sql
    assert "UPDATE Client SET isactive = TRUE WHERE isactive IS NULL" in sql


def test_database_init_seeds_use_logins_and_hashes():
    import re
    sql = (Path(__file__).parent.parent / "docs" / "Database_Init.sql").read_text(encoding="utf-8")
    # таблица Employee содержит колонку Login
    assert re.search(r"CREATE TABLE Employee \(.*?Login VARCHAR", sql, re.DOTALL)
    # INSERT сотрудников содержит логины и 44-символьные хеши, а не plaintext
    emp_start = sql.index("INSERT INTO Employee")
    emp_end = sql.index("-- 3.", emp_start)
    emp_insert = sql[emp_start:emp_end]
    hashes = re.findall(r"'([A-Za-z0-9+/]{43}=)'", emp_insert)
    assert len(hashes) >= 11, f"ожидались хеши паролей, найдено: {len(hashes)}"
    assert "'admin', 'admin'" not in emp_insert and ", 'admin', 'admin'" not in emp_insert
    # таблица Client содержит isactive
    assert re.search(r"CREATE TABLE Client \(.*?isactive BOOLEAN", sql, re.DOTALL)
