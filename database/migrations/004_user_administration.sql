-- Índices para que la administración de usuarios mantenga consultas rápidas.
CREATE INDEX IF NOT EXISTS idx_app_users_active ON app_users (is_active);
CREATE INDEX IF NOT EXISTS idx_app_users_role ON app_users (role);
