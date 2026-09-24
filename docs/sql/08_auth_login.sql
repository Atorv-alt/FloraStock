-- ==========================================
-- 08_auth_login.sql
-- Отдельная колонка login + уникальность.
-- Применяется ПОСЛЕ 06_constraints.sql.
-- Идемпотентно: повторный запуск безопасен.
-- БД, созданные API через EnsureCreated, уже содержат
-- колонку (см. AppDbContext) — скрипт для них no-op.
-- Дополнительно стартует C#-нормализация в Program.cs:
-- backfill пустых login + хеширование plaintext-паролей.
-- ==========================================

-- ---------- 1. Колонка login ----------
ALTER TABLE Employee ADD COLUMN IF NOT EXISTS login VARCHAR(100);

-- ---------- 2. Backfill из email (до @) ----------
UPDATE Employee
SET login = lower(split_part(email, '@', 1))
WHERE (login IS NULL OR btrim(login) = '')
  AND email IS NOT NULL AND email LIKE '%@%.%';

-- Запасной вариант, если email нет: user<ID>
UPDATE Employee
SET login = 'user' || id
WHERE login IS NULL OR btrim(login) = '';

-- ---------- 3. Разрешение коллизий backfill ----------
-- Если два email дали одинаковый login — дописываем ID.
UPDATE Employee e
SET login = login || id
WHERE EXISTS (
    SELECT 1 FROM Employee x
    WHERE lower(x.login) = lower(e.login) AND x.id < e.id
);

-- ---------- 4. Уникальность логина ----------
CREATE UNIQUE INDEX IF NOT EXISTS uq_employee_login ON Employee(login);

-- ---------- Проверка ----------
-- SELECT id, fullname, login, email FROM Employee ORDER BY id;
