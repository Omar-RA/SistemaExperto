CREATE TABLE enfermedades (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    prevalencia_mexico VARCHAR(100),
    muertes_anuales VARCHAR(100),
    fuente VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sintomas (
    id SERIAL PRIMARY KEY,
    enfermedad_id INTEGER REFERENCES enfermedades(id),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    peso INTEGER NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evaluaciones (
    id SERIAL PRIMARY KEY,
    sintomas_ingresados JSONB NOT NULL,
    nivel_riesgo VARCHAR(20) NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    resultado JSONB NOT NULL,
    ip_usuario VARCHAR(45),
    fecha_evaluacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
