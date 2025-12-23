create table if not exists admin_users(
    id integer primary key,
    username text not null,
    password text not null,
    created_at timestamp not null default current_timestamp,
    updated_at timestamp not null default current_timestamp
);

-- 기본 관리자 계정 (비밀번호: admin123)
-- 이미 존재하면 무시 (OR IGNORE는 SQLite 문법)
INSERT OR IGNORE INTO admin_users (id, username, password) 
VALUES (1, 'admin', '$2b$12$uBulCWv7eNuYY8xfp6j4k.3hawRlYSoifJFO.arMQZZINQMWUfkuy');
