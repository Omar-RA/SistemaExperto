-- Insertar la enfermedad
INSERT INTO enfermedades (nombre, descripcion, prevalencia_mexico, muertes_anuales, fuente)
VALUES (
    'Diabetes Mellitus Tipo 2',
    'Enfermedad crónica que afecta la forma en que el cuerpo metaboliza la glucosa. El páncreas no produce suficiente insulina o el cuerpo no la usa correctamente.',
    '14.1% de adultos mayores de 20 años',
    '~115,000 muertes anuales (INEGI 2022)',
    'INEGI, ENSANUT 2022'
);

-- Insertar los 15 síntomas (enfermedad_id = 1)
INSERT INTO sintomas (enfermedad_id, codigo, nombre, descripcion, peso, categoria) VALUES
(1, 'poliuria',               'Orinar frecuentemente (más de 8 veces al día)',       'Necesidad frecuente de orinar, especialmente de noche',              3, 'cardinal'),
(1, 'polidipsia',             'Sed excesiva y persistente',                           'Sed intensa que no se calma aunque se beba agua',                    3, 'cardinal'),
(1, 'perdida_peso',           'Pérdida de peso sin razón aparente',                   'Bajar de peso sin hacer dieta ni ejercicio',                          3, 'cardinal'),
(1, 'polifagia',              'Hambre excesiva aunque haya comido',                   'Sensación de hambre constante incluso después de comer',              2, 'cardinal'),
(1, 'fatiga',                 'Fatiga o cansancio extremo',                           'Cansancio inusual que no mejora con descanso',                        2, 'secundario'),
(1, 'vision_borrosa',         'Visión borrosa',                                       'Dificultad para enfocar objetos, visión nublada',                     2, 'secundario'),
(1, 'cicatrizacion_lenta',    'Heridas que tardan en sanar',                          'Cortadas o llagas que no sanan con normalidad',                       2, 'secundario'),
(1, 'infecciones_frecuentes', 'Infecciones frecuentes (piel, encías, vejiga)',        'Infecciones recurrentes sin causa aparente',                          2, 'secundario'),
(1, 'hormigueo',              'Hormigueo o entumecimiento en manos/pies',             'Sensación de agujas o adormecimiento en extremidades',                2, 'secundario'),
(1, 'piel_oscura',            'Manchas oscuras en cuello o axilas (acantosis nigricans)', 'Piel oscura y aterciopelada en pliegues corporales',             2, 'secundario'),
(1, 'antecedentes_familiares','Familiares directos con diabetes',                     'Padres, hermanos o abuelos con diabetes tipo 2',                      2, 'factor_riesgo'),
(1, 'sobrepeso',              'Sobrepeso u obesidad (IMC > 25)',                      'Índice de masa corporal elevado',                                     2, 'factor_riesgo'),
(1, 'sedentarismo',           'Vida sedentaria (menos de 30 min ejercicio/día)',      'Poca o nula actividad física regular',                                1, 'factor_riesgo'),
(1, 'hipertension',           'Presión arterial alta diagnosticada',                  'Hipertensión arterial previamente diagnosticada',                     1, 'factor_riesgo'),
(1, 'edad_mayor_45',          'Edad mayor de 45 años',                                'El riesgo aumenta significativamente a partir de los 45 años',        1, 'factor_riesgo');