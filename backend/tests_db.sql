BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 706acfea56f9

CREATE TABLE language (
    id SERIAL NOT NULL, 
    name VARCHAR(64) NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE users (
    id SERIAL NOT NULL, 
    username VARCHAR(64) NOT NULL, 
    password VARCHAR(64) NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (username)
);

CREATE TABLE rooms (
    id SERIAL NOT NULL, 
    title VARCHAR(64) NOT NULL, 
    code VARCHAR NOT NULL, 
    invite_link VARCHAR(32) NOT NULL, 
    owner_id INTEGER NOT NULL, 
    language_id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(language_id) REFERENCES language (id), 
    FOREIGN KEY(owner_id) REFERENCES users (id), 
    UNIQUE (invite_link)
);

CREATE TABLE room_members (
    user_id INTEGER NOT NULL, 
    room_id INTEGER NOT NULL, 
    PRIMARY KEY (user_id, room_id), 
    FOREIGN KEY(room_id) REFERENCES rooms (id), 
    FOREIGN KEY(user_id) REFERENCES users (id), 
    UNIQUE (user_id, room_id)
);

INSERT INTO alembic_version (version_num) VALUES ('706acfea56f9') RETURNING alembic_version.version_num;

COMMIT;

