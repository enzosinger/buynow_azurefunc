'''Arquivo para referências de criação de BD e tabela(s)'''

CREATE DATABASE buynow_produtos;
USE buynow_produtos;

CREATE TABLE products (
    pid INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description VARCHAR(300)
);
