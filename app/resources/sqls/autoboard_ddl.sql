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

-- boards
create table if not exists boards(
    id integer primary key,
    name text not null,
    physical_table_name text not null,
    note text,
    is_attach_file boolean not null default 0,
    created_at timestamp not null default current_timestamp,
    updated_at timestamp not null default current_timestamp
);

-- meta_data
create table if not exists meta_data(
    id integer primary key,
    board_id integer not null,
    name text not null, -- `table`,`columns`,`create_edit`,`view`,`list`
    meta text not null, --json format
    schema text not null,
    created_at timestamp not null default current_timestamp,
    updated_at timestamp not null default current_timestamp
);

-- files
create table if not exists files(
    id integer primary key,
    base_folder text not null,
    physical_name text not null,
    logical_name text not null,
    size integer not null,
    mime text not null,
    created_at timestamp not null default current_timestamp,
    updated_at timestamp not null default current_timestamp
);

-- file_match
create table if not exists file_match(
    id integer primary key,
    board_id integer not null,
    table_id integer not null,
    file_id integer not null,
    created_at timestamp not null default current_timestamp,
    updated_at timestamp not null default current_timestamp
);
    