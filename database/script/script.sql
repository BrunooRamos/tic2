-- Script de configuración de la base de datos
-- Este script crea la estructura necesaria para el sistema de monitoreo ambiental

-- Tabla principal que almacena las lecturas de sensores
CREATE TABLE IF NOT EXISTS info (
    -- Identificador único autoincremental
    id SERIAL PRIMARY KEY,
    
    -- ID del Raspberry Pi que generó la lectura
    raspberry_id INTEGER NOT NULL,
    
    -- Cantidad de personas detectadas
    people INTEGER NOT NULL,
    
    -- Lectura de humedad en porcentaje
    humidity INTEGER NOT NULL,
    
    -- Lectura de temperatura en grados Celsius
    temperature INTEGER NOT NULL,
    
    -- Lectura de CO2 en ppm
    co2 INTEGER NOT NULL,
    
    -- Fecha y hora de la lectura (se establece automáticamente)
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Flag que indica si el registro ha sido procesado
    processed BOOLEAN NOT NULL DEFAULT FALSE
);

-- Índices para optimizar consultas comunes
CREATE INDEX IF NOT EXISTS idx_info_processed ON info(processed);
CREATE INDEX IF NOT EXISTS idx_info_timestamp ON info(timestamp);
CREATE INDEX IF NOT EXISTS idx_info_raspberry_id ON info(raspberry_id);

-- Comentarios de la tabla
COMMENT ON TABLE info IS 'Almacena las lecturas de sensores y su estado de procesamiento';
COMMENT ON COLUMN info.id IS 'Identificador único del registro';
COMMENT ON COLUMN info.raspberry_id IS 'ID del Raspberry Pi que generó la lectura';
COMMENT ON COLUMN info.people IS 'Cantidad de personas detectadas';
COMMENT ON COLUMN info.humidity IS 'Lectura de humedad en porcentaje';
COMMENT ON COLUMN info.temperature IS 'Lectura de temperatura en grados Celsius';
COMMENT ON COLUMN info.co2 IS 'Lectura de CO2 en ppm';
COMMENT ON COLUMN info.timestamp IS 'Fecha y hora de la lectura';
COMMENT ON COLUMN info.processed IS 'Indica si el registro ha sido procesado';