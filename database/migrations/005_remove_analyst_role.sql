-- La aplicación trabaja con dos perfiles claros para el MVP: ADMIN y OPERATOR.
UPDATE app_users SET role = 'OPERATOR' WHERE role = 'ANALYST';

ALTER TABLE app_users DROP CONSTRAINT IF EXISTS app_users_role_check;
ALTER TABLE app_users ADD CONSTRAINT app_users_role_check CHECK (role IN ('ADMIN', 'OPERATOR'));
