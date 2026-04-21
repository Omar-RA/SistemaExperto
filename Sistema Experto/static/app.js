// ============================================================
// ESTADO
// ============================================================
let sintomasSeleccionados = new Set();
let catalogoSintomas = {};

// ============================================================
// INICIALIZACIÓN
// ============================================================
async function init() {
  try {
    const res = await fetch('/api/sintomas');
    const data = await res.json();
    catalogoSintomas = data.sintomas;
    renderizarSintomas(data.sintomas);
    cargarEsquemaSQL();
  } catch (e) {
    document.querySelector('.sintomas-section p').textContent =
      '⚠️ No se pudo conectar con el servidor. Verifica que Flask y PostgreSQL estén corriendo.';
  }
}

// ============================================================
// RENDERIZAR SÍNTOMAS
// ============================================================
function renderizarSintomas(sintomas) {
  const categorias = { cardinal: [], secundario: [], factor_riesgo: [] };

  for (const [id, s] of Object.entries(sintomas)) {
    if (categorias[s.categoria]) categorias[s.categoria].push({ id, ...s });
  }

  for (const [cat, items] of Object.entries(categorias)) {
    const container = document.getElementById(`sintomas-${cat}`);
    if (!container) continue;
    container.innerHTML = items.map(s => `
      <div class="sintoma-item" id="item-${s.id}" onclick="toggleSintoma('${s.id}', '${s.nombre.replace(/'/g, "\\'")}')">
        <div class="sintoma-check">
          <svg width="11" height="9" viewBox="0 0 11 9" fill="none">
            <path d="M1 4L4 7L10 1" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="sintoma-info">
          <div class="sintoma-nombre">${s.nombre}</div>
          <div class="sintoma-desc">${s.descripcion}</div>
        </div>
        <div class="peso-badge">×${s.peso}</div>
      </div>
    `).join('');
  }
}

// ============================================================
// SELECCIÓN DE SÍNTOMAS
// ============================================================
function toggleSintoma(id) {
  const el = document.getElementById(`item-${id}`);
  if (sintomasSeleccionados.has(id)) {
    sintomasSeleccionados.delete(id);
    el.classList.remove('selected');
  } else {
    sintomasSeleccionados.add(id);
    el.classList.add('selected');
  }
  actualizarPanel();
}

function actualizarPanel() {
  const n = sintomasSeleccionados.size;
  document.getElementById('contador').textContent = n;
  document.getElementById('btn-evaluar').disabled = n === 0;

  const tagsEl = document.getElementById('selected-tags');
  if (n === 0) {
    tagsEl.innerHTML = '<div style="color:rgba(15,17,23,0.3);font-size:12px;font-family:\'DM Mono\',monospace;text-align:center;padding:10px;">Seleccione síntomas</div>';
    return;
  }

  tagsEl.innerHTML = [...sintomasSeleccionados].map(id => {
    const s = catalogoSintomas[id];
    const nombre = s ? s.nombre.substring(0, 30) + (s.nombre.length > 30 ? '...' : '') : id;
    return `<span class="selected-tag" onclick="toggleSintoma('${id}')">× ${nombre}</span>`;
  }).join('');
}

function limpiarSeleccion() {
  sintomasSeleccionados.forEach(id => {
    document.getElementById(`item-${id}`)?.classList.remove('selected');
  });
  sintomasSeleccionados.clear();
  actualizarPanel();
}

// ============================================================
// EVALUACIÓN
// ============================================================
async function realizarEvaluacion() {
  const btn = document.getElementById('btn-evaluar');
  btn.innerHTML = '<span class="loading"></span>Analizando...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/evaluar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sintomas: [...sintomasSeleccionados] })
    });
    const data = await res.json();
    mostrarResultado(data);
  } catch (e) {
    alert('Error al conectar con el servidor. Verifica que Flask esté corriendo en localhost:5000');
  } finally {
    btn.innerHTML = 'Analizar Síntomas →';
    btn.disabled = false;
  }
}


// ============================================================
// MOSTRAR RESULTADO
// ============================================================
function mostrarResultado(data) {
  const badge  = document.getElementById('res-badge');
  const titulo = document.getElementById('res-titulo');
  const body   = document.getElementById('res-body');

  const nivelKey = data.nivel_riesgo.replace(' ', '');
  badge.className = `riesgo-badge riesgo-${nivelKey}`;
  badge.innerHTML = `● RIESGO ${data.nivel_riesgo} — ${data.urgencia}`;
  titulo.textContent = data.enfermedad;

  const fillClass  = `score-fill-${nivelKey}`;
  const recsHtml   = data.recomendaciones.map(r => `<div class="rec-item">${r}</div>`).join('');
  const nombresRegla = { triada_clasica: 'Tríada Clásica', perdida_con_cardinales: 'Pérdida de Peso + Cardinales', neuropatia_probable: 'Neuropatía Probable' };
  const reglasActivas = Object.entries(data.reglas_activadas)
    .map(([k, v]) => `<span class="regla-tag ${v ? 'regla-activa' : 'regla-inactiva'}">${v ? '✓' : '—'} ${nombresRegla[k]}</span>`)
    .join('');

  body.innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:24px;">
      <div style="text-align:center;padding:16px;background:var(--cream);border-radius:3px;">
        <div style="font-family:'Playfair Display',serif;font-size:28px;font-weight:700;">${data.sintomas_detectados.cardinales.length}</div>
        <div style="font-family:'DM Mono',monospace;font-size:10px;opacity:0.5;letter-spacing:1px;text-transform:uppercase;">Cardinales</div>
      </div>
      <div style="text-align:center;padding:16px;background:var(--cream);border-radius:3px;">
        <div style="font-family:'Playfair Display',serif;font-size:28px;font-weight:700;">${data.sintomas_detectados.secundarios.length}</div>
        <div style="font-family:'DM Mono',monospace;font-size:10px;opacity:0.5;letter-spacing:1px;text-transform:uppercase;">Secundarios</div>
      </div>
      <div style="text-align:center;padding:16px;background:var(--cream);border-radius:3px;">
        <div style="font-family:'Playfair Display',serif;font-size:28px;font-weight:700;">${data.sintomas_detectados.factores_riesgo.length}</div>
        <div style="font-family:'DM Mono',monospace;font-size:10px;opacity:0.5;letter-spacing:1px;text-transform:uppercase;">Factores Riesgo</div>
      </div>
    </div>

    <div class="score-bar-container">
      <div class="score-label">Score de Riesgo Diagnóstico</div>
      <div class="score-bar">
        <div class="score-fill ${fillClass}" style="width:0%" id="score-fill-anim"></div>
      </div>
      <div class="score-value">${data.score}% del máximo posible</div>
    </div>

    <div class="reglas-section">
      <h4>Reglas Activadas</h4>
      ${reglasActivas}
    </div>

    <div class="explicacion-box">
      <strong style="display:block;margin-bottom:6px;font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1px;text-transform:uppercase;opacity:0.6;">Razonamiento del Sistema</strong>
      ${data.explicacion}
    </div>

    <div class="recomendaciones-section">
      <h4>Recomendaciones</h4>
      ${recsHtml}
    </div>

    <div style="display:flex;gap:12px;margin-top:20px;padding:14px;background:var(--cream);border-radius:3px;font-family:'DM Mono',monospace;font-size:11px;color:rgba(15,17,23,0.45);">
      <span>ID: #${data.evaluacion_id}</span>
      <span>·</span>
      <span>${data.fecha_evaluacion}</span>
    </div>

    <div class="disclaimer-box">${data.disclaimer}</div>
  `;

  document.getElementById('resultado-overlay').classList.add('visible');

  setTimeout(() => {
    document.getElementById('score-fill-anim').style.width = `${data.score}%`;
  }, 100);
}

function cerrarModal() {
  document.getElementById('resultado-overlay').classList.remove('visible');
}

function cerrarResultado(e) {
  if (e.target === document.getElementById('resultado-overlay')) cerrarModal();
}

// ============================================================
// TABS
// ============================================================
function switchTab(tab) {
  const indices = { evaluacion: 0, investigacion: 1, sistema: 2, base_datos: 3, historial: 4 };
  document.querySelectorAll('.tab-btn').forEach((b, i) => {
    b.classList.toggle('active', i === indices[tab]);
  });
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.getElementById(`tab-${tab}`).classList.add('active');
  if (tab === 'historial') cargarHistorial();
}

// ============================================================
// HISTORIAL
// ============================================================
async function cargarHistorial() {
  const container = document.getElementById('historial-container');
  try {
    const res  = await fetch('/api/historial');
    const data = await res.json();

    if (data.evaluaciones.length === 0) {
      container.innerHTML = '<div style="text-align:center;padding:60px;color:rgba(15,17,23,0.35);font-family:\'DM Mono\',monospace;font-size:13px;">Aún no hay evaluaciones registradas</div>';
      return;
    }

    const colores = { 'ALTO': '#b01c00', 'MODERADO': '#b06500', 'BAJO': '#7a6000', 'MUY BAJO': '#1a6b3a' };
    container.innerHTML = data.evaluaciones.map(r => `
      <div class="hist-card">
        <div class="hist-id">#${r.id}</div>
        <div class="hist-score" style="color:${colores[r.nivel_riesgo] || '#333'}">${r.score}%</div>
        <div class="hist-info">
          <strong>Riesgo ${r.nivel_riesgo}</strong>
          <span>${r.num_sintomas} síntomas · ${new Date(r.fecha).toLocaleString('es-MX')}</span>
        </div>
      </div>
    `).join('');
  } catch (e) {
    container.innerHTML = '<div style="text-align:center;padding:40px;color:rgba(15,17,23,0.35);font-family:\'DM Mono\',monospace;font-size:12px;">Servidor no disponible en modo demo</div>';
  }
}

// ============================================================
// ESQUEMA SQL
// ============================================================
async function cargarEsquemaSQL() {
  try {
    const res  = await fetch('/api/esquema_sql');
    const data = await res.json();
    const el   = document.getElementById('sql-schema');
    const sql  = data.esquema
      .replace(/\b(CREATE|TABLE|PRIMARY|KEY|SERIAL|INTEGER|VARCHAR|TEXT|DECIMAL|JSONB|TIMESTAMP|DEFAULT|CURRENT_TIMESTAMP|REFERENCES|NOT|NULL|UNIQUE|VIEW|SELECT|FROM|WHERE|GROUP|BY|COUNT|AVG|DATE|AS|AND)\b/g,
        '<span class="sql-keyword">$1</span>')
      .replace(/--[^\n]*/g, '<span class="sql-comment">$&</span>');
    el.innerHTML = sql;
  } catch (e) {
    document.getElementById('sql-schema').textContent =
      '⚠️ No se pudo cargar el esquema. Verifica la conexión con PostgreSQL.';
  }
}

// ============================================================
// INICIO
// ============================================================
init();
actualizarPanel();
