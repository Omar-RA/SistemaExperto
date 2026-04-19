from flask import Flask, request, jsonify, render_template
from datetime import datetime
import json
import os

app = Flask(__name__)

# ============================================================
# BASE DE CONOCIMIENTO - DIABETES MELLITUS TIPO 2
# ============================================================
# Justificación: La diabetes es la 2ª causa de muerte en México
# (INEGI 2022), con ~115,000 muertes anuales. Es prevenible y
# tratable si se detecta a tiempo. México tiene una de las tasas
# más altas del mundo (14.1% de adultos).

ENFERMEDAD = {
    "nombre": "Diabetes Mellitus Tipo 2",
    "descripcion": "Enfermedad crónica que afecta la forma en que el cuerpo metaboliza la glucosa (azúcar). El páncreas no produce suficiente insulina o el cuerpo no la usa correctamente.",
    "prevalencia_mexico": "14.1% de adultos mayores de 20 años",
    "muertes_anuales": "~115,000 muertes anuales (INEGI 2022)",
    "fuente": "INEGI, ENSANUT 2022"
}

# Síntomas con sus pesos y umbrales de riesgo
SINTOMAS = {
    "poliuria": {
        "nombre": "Orinar frecuentemente (más de 8 veces al día)",
        "peso": 3,
        "descripcion": "Necesidad frecuente de orinar, especialmente de noche",
        "categoria": "cardinal"
    },
    "polidipsia": {
        "nombre": "Sed excesiva y persistente",
        "peso": 3,
        "descripcion": "Sed intensa que no se calma aunque se beba agua",
        "categoria": "cardinal"
    },
    "polifagia": {
        "nombre": "Hambre excesiva aunque haya comido",
        "peso": 2,
        "descripcion": "Sensación de hambre constante incluso después de comer",
        "categoria": "cardinal"
    },
    "perdida_peso": {
        "nombre": "Pérdida de peso sin razón aparente",
        "peso": 3,
        "descripcion": "Bajar de peso sin hacer dieta ni ejercicio",
        "categoria": "cardinal"
    },
    "fatiga": {
        "nombre": "Fatiga o cansancio extremo",
        "peso": 2,
        "descripcion": "Cansancio inusual que no mejora con descanso",
        "categoria": "secundario"
    },
    "vision_borrosa": {
        "nombre": "Visión borrosa",
        "peso": 2,
        "descripcion": "Dificultad para enfocar objetos, visión nublada",
        "categoria": "secundario"
    },
    "cicatrizacion_lenta": {
        "nombre": "Heridas que tardan en sanar",
        "peso": 2,
        "descripcion": "Cortadas, llagas o moretones que no sanan con normalidad",
        "categoria": "secundario"
    },
    "infecciones_frecuentes": {
        "nombre": "Infecciones frecuentes (piel, encías, vejiga)",
        "peso": 2,
        "descripcion": "Infecciones recurrentes sin causa aparente",
        "categoria": "secundario"
    },
    "hormigueo": {
        "nombre": "Hormigueo o entumecimiento en manos/pies",
        "peso": 2,
        "descripcion": "Sensación de agujas o adormecimiento en extremidades",
        "categoria": "secundario"
    },
    "piel_oscura": {
        "nombre": "Manchas oscuras en cuello o axilas (acantosis nigricans)",
        "peso": 2,
        "descripcion": "Piel oscura y aterciopelada en pliegues corporales",
        "categoria": "secundario"
    },
    "antecedentes_familiares": {
        "nombre": "Familiares directos con diabetes",
        "peso": 2,
        "descripcion": "Padres, hermanos o abuelos con diabetes tipo 2",
        "categoria": "factor_riesgo"
    },
    "sobrepeso": {
        "nombre": "Sobrepeso u obesidad (IMC > 25)",
        "peso": 2,
        "descripcion": "Índice de masa corporal elevado",
        "categoria": "factor_riesgo"
    },
    "sedentarismo": {
        "nombre": "Vida sedentaria (menos de 30 min ejercicio/día)",
        "peso": 1,
        "descripcion": "Poca o nula actividad física regular",
        "categoria": "factor_riesgo"
    },
    "hipertension": {
        "nombre": "Presión arterial alta diagnosticada",
        "peso": 1,
        "descripcion": "Hipertensión arterial previamente diagnosticada",
        "categoria": "factor_riesgo"
    },
    "edad_mayor_45": {
        "nombre": "Edad mayor de 45 años",
        "peso": 1,
        "descripcion": "El riesgo aumenta significativamente a partir de los 45 años",
        "categoria": "factor_riesgo"
    }
}

# ============================================================
# MOTOR DE INFERENCIA - REGLAS IF-THEN
# ============================================================

def evaluar_sintomas(sintomas_presentes: list) -> dict:
    """
    Motor de inferencia basado en reglas if-then.
    Evalúa síntomas y calcula nivel de riesgo de diabetes.
    """
    
    score_total = 0
    score_maximo = sum(s["peso"] for s in SINTOMAS.values())
    sintomas_cardinales_presentes = []
    factores_riesgo_presentes = []
    sintomas_secundarios_presentes = []
    
    # REGLA 1: Clasificar síntomas y acumular puntaje
    for sintoma_id in sintomas_presentes:
        if sintoma_id in SINTOMAS:
            datos = SINTOMAS[sintoma_id]
            score_total += datos["peso"]
            
            if datos["categoria"] == "cardinal":
                sintomas_cardinales_presentes.append(sintoma_id)
            elif datos["categoria"] == "factor_riesgo":
                factores_riesgo_presentes.append(sintoma_id)
            else:
                sintomas_secundarios_presentes.append(sintoma_id)
    
    porcentaje = (score_total / score_maximo) * 100
    
    # REGLA 2: Síntomas cardinales clásicos (tríada diagnóstica)
    triada_clasica = all(s in sintomas_presentes for s in ["poliuria", "polidipsia", "polifagia"])
    
    # REGLA 3: Pérdida de peso + síntomas cardinales
    perdida_con_cardinales = "perdida_peso" in sintomas_presentes and len(sintomas_cardinales_presentes) >= 2
    
    # REGLA 4: Síntomas neurológicos (complicación)
    neuropatia_probable = "hormigueo" in sintomas_presentes and ("fatiga" in sintomas_presentes or "vision_borrosa" in sintomas_presentes)
    
    # REGLA 5: Determinar nivel de riesgo
    if triada_clasica or perdida_con_cardinales or porcentaje >= 60:
        nivel_riesgo = "ALTO"
        color = "rojo"
        urgencia = "URGENTE"
    elif len(sintomas_cardinales_presentes) >= 2 or porcentaje >= 35:
        nivel_riesgo = "MODERADO"
        color = "naranja"
        urgencia = "PRONTO"
    elif len(sintomas_presentes) >= 2 or porcentaje >= 15:
        nivel_riesgo = "BAJO"
        color = "amarillo"
        urgencia = "PREVENTIVO"
    else:
        nivel_riesgo = "MUY BAJO"
        color = "verde"
        urgencia = "MONITOREO"
    
    # REGLA 6: Generar recomendaciones específicas
    recomendaciones = generar_recomendaciones(
        nivel_riesgo, 
        sintomas_cardinales_presentes,
        factores_riesgo_presentes,
        neuropatia_probable
    )
    
    # REGLA 7: Explicación del razonamiento
    explicacion = generar_explicacion(
        sintomas_presentes,
        sintomas_cardinales_presentes,
        factores_riesgo_presentes,
        triada_clasica,
        perdida_con_cardinales,
        neuropatia_probable,
        porcentaje
    )
    
    return {
        "enfermedad": ENFERMEDAD["nombre"],
        "nivel_riesgo": nivel_riesgo,
        "color": color,
        "urgencia": urgencia,
        "score": round(porcentaje, 1),
        "sintomas_detectados": {
            "cardinales": sintomas_cardinales_presentes,
            "secundarios": sintomas_secundarios_presentes,
            "factores_riesgo": factores_riesgo_presentes
        },
        "reglas_activadas": {
            "triada_clasica": triada_clasica,
            "perdida_con_cardinales": perdida_con_cardinales,
            "neuropatia_probable": neuropatia_probable
        },
        "recomendaciones": recomendaciones,
        "explicacion": explicacion,
        "disclaimer": "⚠️ Este sistema NO reemplaza un diagnóstico médico. Consulte a un profesional de salud.",
        "fecha_evaluacion": datetime.now().strftime("%d/%m/%Y %H:%M")
    }


def generar_recomendaciones(nivel, cardinales, factores, neuropatia):
    recs = []
    
    if nivel == "ALTO":
        recs.append("🚨 Acuda a consulta médica en los próximos 1-2 días")
        recs.append("📋 Solicite análisis de glucosa en sangre en ayunas y HbA1c")
        recs.append("🩺 Hable con su médico sobre la posibilidad de diabetes")
    elif nivel == "MODERADO":
        recs.append("👨‍⚕️ Programe una cita médica esta semana")
        recs.append("🔬 Solicite una prueba de glucosa en ayunas")
        recs.append("📊 Monitoree sus síntomas diariamente")
    elif nivel == "BAJO":
        recs.append("📅 Consulte a su médico en su próxima cita de rutina")
        recs.append("🧪 Considere hacer una prueba de glucosa preventiva")
    else:
        recs.append("✅ Mantenga hábitos saludables como prevención")
        recs.append("📅 Realice chequeos médicos anuales")
    
    if "antecedentes_familiares" in factores:
        recs.append("👨‍👩‍👧 Con antecedentes familiares, haga pruebas de glucosa cada 6 meses")
    if "sobrepeso" in factores:
        recs.append("🥗 Reduzca el consumo de azúcares y carbohidratos refinados")
    if "sedentarismo" in factores:
        recs.append("🚶 Realice al menos 30 minutos de actividad física moderada al día")
    if neuropatia:
        recs.append("⚡ Los síntomas neurológicos requieren evaluación médica urgente")
    
    recs.append("💧 Mantenga una hidratación adecuada (2L de agua al día)")
    recs.append("🚫 Evite bebidas azucaradas, refrescos y alimentos ultraprocesados")
    
    return recs


def generar_explicacion(presentes, cardinales, factores, triada, perdida, neuropatia, porcentaje):
    partes = []
    
    if triada:
        partes.append("Se detectó la TRÍADA CLÁSICA de diabetes (poliuria + polidipsia + polifagia), que es el patrón diagnóstico más significativo.")
    
    if perdida:
        partes.append(f"La pérdida de peso inexplicable combinada con {len(cardinales)} síntoma(s) cardinal(es) eleva significativamente el riesgo.")
    
    if len(cardinales) > 0:
        partes.append(f"Se presentaron {len(cardinales)} síntoma(s) cardinal(es) de alto valor diagnóstico.")
    
    if len(factores) > 0:
        partes.append(f"Se identificaron {len(factores)} factor(es) de riesgo que aumentan la probabilidad.")
    
    if neuropatia:
        partes.append("Los síntomas neurológicos (hormigueo + fatiga/visión borrosa) sugieren posible afectación del sistema nervioso asociada a glucosa elevada.")
    
    partes.append(f"El puntaje total de síntomas es {porcentaje:.1f}% del máximo posible.")
    
    return " ".join(partes) if partes else "Pocos síntomas detectados. Se recomienda monitoreo preventivo."


# ============================================================
# ALMACENAMIENTO EN MEMORIA (Simula PostgreSQL)
# ============================================================
# Nota: En producción real se usaría PostgreSQL con psycopg2
# Estructura equivalente a las tablas SQL definidas abajo

historial_consultas = []  # Simula tabla: evaluaciones
id_counter = 1

# Equivalente SQL de las tablas:
ESQUEMA_SQL = """
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

-- Vista: Estadísticas por nivel de riesgo
CREATE VIEW estadisticas_riesgo AS
SELECT 
    nivel_riesgo,
    COUNT(*) as total_casos,
    AVG(score) as score_promedio,
    DATE(fecha_evaluacion) as fecha
FROM evaluaciones
GROUP BY nivel_riesgo, DATE(fecha_evaluacion);
"""

def guardar_evaluacion(sintomas_ingresados, resultado):
    global id_counter
    registro = {
        "id": id_counter,
        "sintomas_ingresados": sintomas_ingresados,
        "nivel_riesgo": resultado["nivel_riesgo"],
        "score": resultado["score"],
        "resultado": resultado,
        "fecha_evaluacion": datetime.now().isoformat()
    }
    historial_consultas.append(registro)
    id_counter += 1
    return registro["id"]


# ============================================================
# RUTAS API FLASK
# ============================================================

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/api/evaluar", methods=["POST"])
def evaluar():
    """Recibe síntomas en JSON y devuelve diagnóstico"""
    data = request.get_json()
    if not data or "sintomas" not in data:
        return jsonify({"error": "Se requiere un campo 'sintomas' con lista de síntomas"}), 400
    
    sintomas = data["sintomas"]
    if not isinstance(sintomas, list):
        return jsonify({"error": "El campo 'sintomas' debe ser una lista"}), 400
    
    resultado = evaluar_sintomas(sintomas)
    evaluacion_id = guardar_evaluacion(sintomas, resultado)
    resultado["evaluacion_id"] = evaluacion_id
    
    return jsonify(resultado)

@app.route("/api/sintomas", methods=["GET"])
def listar_sintomas():
    """Lista todos los síntomas disponibles"""
    return jsonify({
        "sintomas": SINTOMAS,
        "enfermedad": ENFERMEDAD
    })

@app.route("/api/historial", methods=["GET"])
def obtener_historial():
    """Devuelve historial de evaluaciones"""
    resumen = [
        {
            "id": r["id"],
            "nivel_riesgo": r["nivel_riesgo"],
            "score": r["score"],
            "num_sintomas": len(r["sintomas_ingresados"]),
            "fecha": r["fecha_evaluacion"]
        }
        for r in historial_consultas[-20:]  # Últimas 20
    ]
    return jsonify({
        "total": len(historial_consultas),
        "evaluaciones": resumen
    })

@app.route("/api/estadisticas", methods=["GET"])
def estadisticas():
    """Estadísticas del sistema"""
    if not historial_consultas:
        return jsonify({"mensaje": "Sin datos aún"})
    
    por_nivel = {}
    for r in historial_consultas:
        nivel = r["nivel_riesgo"]
        por_nivel[nivel] = por_nivel.get(nivel, 0) + 1
    
    scores = [r["score"] for r in historial_consultas]
    
    return jsonify({
        "total_evaluaciones": len(historial_consultas),
        "distribucion_riesgo": por_nivel,
        "score_promedio": round(sum(scores) / len(scores), 1),
        "score_maximo": max(scores),
        "score_minimo": min(scores)
    })

@app.route("/api/esquema_sql", methods=["GET"])
def esquema_sql():
    """Devuelve el esquema SQL equivalente"""
    return jsonify({"esquema": ESQUEMA_SQL})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
