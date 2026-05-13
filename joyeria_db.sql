CREATE DATABASE IF NOT EXISTS joyeria_db;
USE joyeria_db;

CREATE TABLE IF NOT EXISTS jewelryitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    material VARCHAR(50) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0
);

INSERT INTO jewelryitem (nombre, categoria, material, precio, stock) VALUES 
('Cadena de Eslabones', 'Collar', 'Plata 925', 450.00, 15),
('Anillo de Compromiso Clásico', 'Anillo', 'Oro Blanco 14k', 3200.50, 3),
('Pulsera Minimalista', 'Pulsera', 'Acero Inoxidable', 150.00, 30),
('Aretes de Perla', 'Aretes', 'Plata 925', 280.00, 12);