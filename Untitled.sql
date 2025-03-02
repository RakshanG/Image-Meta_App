CREATE TABLE metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT,
    key_name VARCHAR(255),
    value TEXT,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);
SHOW TABLES;

CREATE TABLE images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT,
    key_name VARCHAR(255),
    value TEXT,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

SELECT * FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_NAME = 'metadata';

SHOW CREATE TABLE images;
SHOW CREATE TABLE metadata;

SHOW TABLES;

SHOW CREATE TABLE images;
SHOW CREATE TABLE metadata;

DROP TABLE IF EXISTS metadata;


SELECT * FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_NAME = 'metadata';

SHOW CREATE TABLE images;


SELECT * FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_NAME = 'metadata';

INSERT INTO metadata (image_id, key_name, value) VALUES (1, 'Test Key', 'Test Value');

SELECT * FROM images;
INSERT INTO images (user_id, filename, file_path) VALUES (1, 'sample.jpg', '/path/to/sample.jpg');
INSERT INTO metadata (image_id, key_name, value) VALUES (LAST_INSERT_ID(), 'Test Key', 'Test Value');

SELECT * FROM metadata WHERE image_id NOT IN (SELECT id FROM images);

SET SQL_SAFE_UPDATES = 0;
DELETE FROM metadata WHERE image_id NOT IN (SELECT id FROM images);


SELECT * FROM images;
SELECT * FROM metadata;
SELECT m.* 
FROM metadata m
LEFT JOIN images i ON m.image_id = i.id
WHERE i.id IS NULL;


INSERT INTO images (user_id, filename, file_path) VALUES (2, 'test.jpg', '/path/to/test.jpg');

INSERT INTO metadata (image_id, key_name, value) 
VALUES (LAST_INSERT_ID(), 'Camera Model', 'Canon EOS R5');



SELECT * FROM images;
INSERT INTO images (user_id, filename, file_path) 
VALUES (1, 'sample.jpg', '/path/to/sample.jpg');
SELECT LAST_INSERT_ID();


INSERT INTO metadata (image_id, key_name, value) 
VALUES (2, 'Test Key', 'Test Value');

SELECT * FROM metadata WHERE image_id NOT IN (SELECT id FROM images);


SELECT * FROM images;

INSERT INTO images (user_id, filename, file_path) 
VALUES (1, 'sample.jpg', '/path/to/sample.jpg');

SELECT LAST_INSERT_ID();

INSERT INTO metadata (image_id, key_name, value) 
VALUES (3, 'Test Key', 'Test Value');

SELECT * FROM metadata;

SELECT * FROM images;

DELETE FROM images WHERE id = 2;
SELECT * FROM metadata; -- Metadata for image_id = 2 should be gone

CREATE DATABASE IF NOT EXISTS image_metadata_db;
USE image_metadata_db;

-- Users Table (For Authentication)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Images Table (Stores Uploaded Image Data)
CREATE TABLE IF NOT EXISTS images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Metadata Table (Stores Extracted Metadata)
CREATE TABLE IF NOT EXISTS metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT NOT NULL,
    key_name VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

DESC metadata;
SELECT * FROM metadata LIMIT 5;

DROP TABLE metadata;

CREATE DATABASE IF NOT EXISTS image_metadata_db;
USE image_metadata_db;

-- Users Table (For Authentication)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Images Table (Stores Uploaded Image Data)
CREATE TABLE IF NOT EXISTS images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Metadata Table (Stores Extracted Metadata)
CREATE TABLE IF NOT EXISTS metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT NOT NULL,
    key_name VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

SHOW TABLES;

SELECT * FROM images ORDER BY id DESC LIMIT 5;
SELECT * FROM metadata ORDER BY image_id DESC LIMIT 5;


INSERT INTO metadata (image_id, key_name, value) 
VALUES (1, 'TestKey', 'TestValue');

SELECT * FROM images ORDER BY id DESC LIMIT 5;

SELECT * FROM metadata ORDER BY image_id DESC LIMIT 5;
