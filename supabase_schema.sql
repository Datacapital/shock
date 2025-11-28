-- ============================================
-- SCHEMA DE BASE DE DATOS PARA SUPABASE
-- Dashboard de Renta Variable
-- ============================================

-- Tabla de acciones
CREATE TABLE IF NOT EXISTS acciones (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(200),
    acciones_circulacion BIGINT,
    activa BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de precios históricos BVC
CREATE TABLE IF NOT EXISTS precios_bvc (
    id SERIAL PRIMARY KEY,
    accion_codigo VARCHAR(20) NOT NULL,
    fecha DATE NOT NULL,
    precio_cierre_bs DECIMAL(20, 4),
    precio_cierre_usd_oficial DECIMAL(20, 4),
    precio_cierre_usd_paralelo DECIMAL(20, 4),
    monto_efectivo_usd_oficial DECIMAL(20, 2),
    monto_efectivo_usd_paralelo DECIMAL(20, 2),
    num_operaciones INTEGER,
    titulos_negociados BIGINT,
    capitalizacion_oficial DECIMAL(20, 2),
    capitalizacion_paralelo DECIMAL(20, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(accion_codigo, fecha),
    FOREIGN KEY (accion_codigo) REFERENCES acciones(codigo) ON DELETE CASCADE
);

-- Tabla de tasas de cambio
CREATE TABLE IF NOT EXISTS tasas_cambio (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE,
    tasa_oficial DECIMAL(10, 4),
    tasa_paralelo DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de configuración
CREATE TABLE IF NOT EXISTS configuracion (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT,
    descripcion TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_precios_bvc_fecha ON precios_bvc(fecha DESC);
CREATE INDEX idx_precios_bvc_accion ON precios_bvc(accion_codigo);
CREATE INDEX idx_tasas_fecha ON tasas_cambio(fecha DESC);

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_acciones_updated_at BEFORE UPDATE ON acciones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insertar configuración inicial
INSERT INTO configuracion (clave, valor, descripcion) VALUES
('hora_actualizacion_bvc', '17:00', 'Hora para actualizar precios BVC (formato HH:MM)'),
('timezone', 'America/Caracas', 'Zona horaria para las actualizaciones'),
('ultima_actualizacion_bvc', NULL, 'Última actualización de precios BVC')
ON CONFLICT (clave) DO NOTHING;

-- Función para obtener el resumen de una acción
CREATE OR REPLACE FUNCTION get_resumen_accion(p_codigo VARCHAR)
RETURNS TABLE (
    codigo VARCHAR,
    nombre VARCHAR,
    precio_actual_oficial DECIMAL,
    precio_actual_paralelo DECIMAL,
    variacion_dia_oficial DECIMAL,
    variacion_dia_paralelo DECIMAL,
    capitalizacion_oficial DECIMAL,
    capitalizacion_paralelo DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.codigo,
        a.nombre,
        (SELECT precio_cierre_usd_oficial FROM precios_bvc 
         WHERE accion_codigo = p_codigo ORDER BY fecha DESC LIMIT 1),
        (SELECT precio_cierre_usd_paralelo FROM precios_bvc 
         WHERE accion_codigo = p_codigo ORDER BY fecha DESC LIMIT 1),
        (SELECT 
            CASE WHEN LAG(precio_cierre_usd_oficial) OVER (ORDER BY fecha) IS NOT NULL
            THEN ((precio_cierre_usd_oficial - LAG(precio_cierre_usd_oficial) OVER (ORDER BY fecha)) 
                  / LAG(precio_cierre_usd_oficial) OVER (ORDER BY fecha) * 100)
            ELSE 0 END
         FROM precios_bvc 
         WHERE accion_codigo = p_codigo ORDER BY fecha DESC LIMIT 1),
        (SELECT 
            CASE WHEN LAG(precio_cierre_usd_paralelo) OVER (ORDER BY fecha) IS NOT NULL
            THEN ((precio_cierre_usd_paralelo - LAG(precio_cierre_usd_paralelo) OVER (ORDER BY fecha)) 
                  / LAG(precio_cierre_usd_paralelo) OVER (ORDER BY fecha) * 100)
            ELSE 0 END
         FROM precios_bvc 
         WHERE accion_codigo = p_codigo ORDER BY fecha DESC LIMIT 1),
        (SELECT capitalizacion_oficial FROM precios_bvc 
         WHERE accion_codigo = p_codigo ORDER BY fecha DESC LIMIT 1),
        (SELECT capitalizacion_paralelo FROM precios_bvc 
         WHERE accion_codigo = p_codigo ORDER BY fecha DESC LIMIT 1)
    FROM acciones a
    WHERE a.codigo = p_codigo;
END;
$$ LANGUAGE plpgsql;
