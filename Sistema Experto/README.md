# Sistema Experto — Detección Temprana de Diabetes Mellitus Tipo 2

## Descripción
Sistema experto desarrollado en Python + Flask para detectar síntomas tempranos de **Diabetes Mellitus Tipo 2**, la segunda causa de muerte en México con más de 115,000 muertes anuales (INEGI 2022).

---

## Investigación: 5 Principales Causas de Muerte en México (INEGI 2022)

| Rango | Enfermedad | Muertes/año | Síntomas iniciales |
|-------|-----------|-------------|-------------------|
| 1 | Enfermedades del corazón | ~140,000 | Dolor torácico, disnea, palpitaciones |
| **2** | **Diabetes Mellitus Tipo 2** ✓ | **~115,000** | **Poliuria, polidipsia, polifagia, fatiga** |
| 3 | Enf. respiratorias / COVID | ~95,000 | Fiebre, tos seca, disnea |
| 4 | Tumores malignos | ~90,000 | Pérdida de peso, fatiga, bultos |
| 5 | Enfermedades del hígado | ~42,000 | Ictericia, ascitis, fatiga extrema |

**Justificación de la selección:** La diabetes fue elegida por su alta prevalencia (14.1% de adultos mexicanos), síntomas claramente identificables, alto potencial de prevención y la claridad de sus reglas diagnósticas, que permiten un motor de inferencia if-then robusto.

---

## Estructura del Proyecto

```
sistema_experto/
├── app.py              # Aplicación Flask + Motor de inferencia
├── index.html          # Interfaz de usuario
├── requirements.txt    # Dependencias
└── README.md           # Documentación
```

---

## Instalación y Ejecución

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python app.py

# 4. Abrir en navegador
http://localhost:5000
```

---

## API REST — Endpoints

### POST /api/evaluar
Recibe síntomas y devuelve diagnóstico.

**Request:**
```json
{
  "sintomas": ["poliuria", "polidipsia", "polifagia", "fatiga"]
}
```

**Response:**
```json
{
  "enfermedad": "Diabetes Mellitus Tipo 2",
  "nivel_riesgo": "ALTO",
  "urgencia": "URGENTE",
  "score": 43.2,
  "reglas_activadas": {
    "triada_clasica": true,
    "perdida_con_cardinales": false,
    "neuropatia_probable": false
  },
  "recomendaciones": ["🚨 Acuda a consulta médica en los próximos 1-2 días", "..."],
  "explicacion": "Se detectó la TRÍADA CLÁSICA de diabetes...",
  "disclaimer": "⚠️ Este sistema NO reemplaza un diagnóstico médico."
}
```

### GET /api/sintomas
Lista el catálogo de 15 síntomas con sus pesos y categorías.

### GET /api/historial
Últimas 20 evaluaciones almacenadas.

### GET /api/estadisticas
Distribución de riesgo y scores promedio.

### GET /api/esquema_sql
Esquema PostgreSQL de las 3 tablas del sistema.

---

## Base de Conocimiento — Síntomas (15 indicadores)

### Síntomas Cardinales (peso 2-3)
| Código | Nombre | Peso |
|--------|--------|------|
| poliuria | Orinar frecuentemente | 3 |
| polidipsia | Sed excesiva y persistente | 3 |
| perdida_peso | Pérdida de peso sin razón | 3 |
| polifagia | Hambre excesiva | 2 |

### Síntomas Secundarios (peso 2)
| Código | Nombre |
|--------|--------|
| fatiga | Fatiga o cansancio extremo |
| vision_borrosa | Visión borrosa |
| cicatrizacion_lenta | Heridas que tardan en sanar |
| infecciones_frecuentes | Infecciones frecuentes |
| hormigueo | Hormigueo en manos/pies |
| piel_oscura | Manchas oscuras (acantosis nigricans) |

### Factores de Riesgo (peso 1-2)
| Código | Peso |
|--------|------|
| antecedentes_familiares | 2 |
| sobrepeso | 2 |
| sedentarismo | 1 |
| hipertension | 1 |
| edad_mayor_45 | 1 |

---

## Motor de Inferencia — Reglas IF-THEN

```python
# REGLA 1: Acumular score ponderado
for sintoma in sintomas_presentes:
    score += SINTOMAS[sintoma]["peso"]

# REGLA 2: Tríada clásica diagnóstica
IF "poliuria" AND "polidipsia" AND "polifagia":
    THEN nivel_riesgo = "ALTO"

# REGLA 3: Pérdida de peso + cardinales
IF "perdida_peso" AND len(cardinales) >= 2:
    THEN nivel_riesgo = "ALTO"

# REGLA 4: Neuropatía probable
IF "hormigueo" AND ("fatiga" OR "vision_borrosa"):
    THEN neuropatia_probable = True

# REGLA 5: Umbral de score
IF score_pct >= 60%: THEN nivel = "ALTO"
IF score_pct >= 35%: THEN nivel = "MODERADO"  
IF score_pct >= 15%: THEN nivel = "BAJO"
ELSE:                     nivel = "MUY BAJO"

# REGLA 6-7: Recomendaciones y explicación por contexto
```

---

## Esquema PostgreSQL

```sql
-- Tabla 1: Enfermedades
CREATE TABLE enfermedades (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    prevalencia_mexico VARCHAR(100),
    muertes_anuales VARCHAR(100),
    fuente VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla 2: Síntomas
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

-- Tabla 3: Registros de evaluación
CREATE TABLE evaluaciones (
    id SERIAL PRIMARY KEY,
    sintomas_ingresados JSONB NOT NULL,
    nivel_riesgo VARCHAR(20) NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    resultado JSONB NOT NULL,
    ip_usuario VARCHAR(45),
    fecha_evaluacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Cómo Funciona el Sistema

1. **El usuario** selecciona síntomas presentes en la interfaz web
2. **La interfaz** envía `POST /api/evaluar` con la lista de síntomas
3. **Flask** recibe el JSON y llama al motor de inferencia
4. **El motor** aplica 7 reglas if-then en secuencia:
   - Clasifica síntomas por categoría
   - Acumula score ponderado
   - Verifica reglas de patrón (tríada, neuropatía)
   - Determina nivel de riesgo por umbrales
   - Genera recomendaciones específicas al contexto
5. **El resultado** se devuelve como JSON y se muestra en la interfaz
6. **La evaluación** se almacena en el historial (PostgreSQL en producción)

---

## Limitaciones del Sistema

- ❌ **No es diagnóstico definitivo** — requiere confirmación médica profesional
- ❌ **Síntomas subjetivos** — la percepción del paciente puede variar
- ❌ **Sin datos numéricos** — no incorpora valores de glucosa, IMC real ni HbA1c
- ❌ **Sin comorbilidades** — no considera otras enfermedades simultáneas
- ❌ **Reglas fijas** — no aprende de nuevos casos (no es ML)
- ❌ **Sin contexto temporal** — no evalúa duración o progresión de síntomas
- ❌ **Sin validación clínica formal** — las reglas están basadas en literatura médica pero no validadas epidemiológicamente

---

## Fuentes

- INEGI (2022). Estadísticas de Mortalidad en México.
- ENSANUT (2022). Encuesta Nacional de Salud y Nutrición.
- NOM-015-SSA2-2010. Para la prevención, tratamiento y control de la diabetes mellitus.
- American Diabetes Association (ADA). Standards of Medical Care in Diabetes, 2023.
