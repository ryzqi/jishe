-- 更新用户表，添加新的字段
ALTER TABLE jishe.user
ADD COLUMN IF NOT EXISTS email VARCHAR(100) UNIQUE NOT NULL DEFAULT 'default@example.com',
ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN NOT NULL DEFAULT FALSE;

-- 创建索引
CREATE INDEX IF NOT EXISTS ix_user_email ON jishe.user(email);

-- 填充已有数据的默认值
UPDATE jishe.user
SET email = CONCAT(username, '@example.com')
WHERE email = 'default@example.com';

-- 注释
COMMENT ON COLUMN jishe.user.email IS '用户电子邮件';
COMMENT ON COLUMN jishe.user.is_active IS '用户是否活跃';
COMMENT ON COLUMN jishe.user.is_superuser IS '是否为超级管理员'; 