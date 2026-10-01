SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
) DEFAULT CHARACTER SET utf8mb4;

INSERT INTO clients (name) VALUES
    ('Alice Martin'),
    ('Bob Dupont'),
    ('Chloé Bernard');
