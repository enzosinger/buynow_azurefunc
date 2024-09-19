'''Arquivo para referências de criação de BD e tabela(s)'''

CREATE DATABASE produtos_db;
USE produtos_db;

CREATE TABLE products (
    pid INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description VARCHAR(300)
);