-- ==========================================
-- 09_client_is_active.sql
-- Флаг активности клиента (isactive).
-- Применяется ПОСЛЕ 06_constraints.sql.
-- Идемпотентно: повторный запуск безопасен.
-- БД, созданные API через EnsureCreated, уже содержат
-- колонку (см. AppDbContext) — скрипт для них no-op.
-- ==========================================

-- ---------- 1. Колонка isactive ----------
ALTER TABLE Client ADD COLUMN IF NOT EXISTS isactive BOOLEAN DEFAULT TRUE;

-- ---------- 2. Backfill для старых строк ----------
UPDATE Client SET isactive = TRUE WHERE isactive IS NULL;

-- ---------- Проверка ----------
-- SELECT id, fullname, email, isactive FROM Client ORDER BY id;
