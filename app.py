import streamlit as st
import whisper
import tempfile
import os
import subprocess
import uuid
from pathlib import Path

# ── Configuración de la página ────────────────────────────────────────────────
st.set_page_config(
    page_title="TranscribeThat",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Estilos CSS TOTALMENTE NUEVOS (Dark Mode) ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Reset y tipografía base */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Fondo principal oscuro */
.stApp {
    background-color: #0E1117 !important;
}

/* Ocultar elementos innecesarios de Streamlit */
#MainMenu, footer, header, [data-testid="collapsedControl"] { 
    display: none !important; 
}

/* Ajuste de márgenes principales para no apretar el contenido */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 95% !important;
}

/* ── NAVBAR MODERNA ── */
.navbar {
    display: flex; align-items: center; justify-content: space-between;
    background: #161B22; border-bottom: 1px solid #30363D;
    padding: 12px 32px; border-radius: 12px; margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.navbar-logo { 
    display: flex; align-items: center; gap: 12px; 
    font-weight: 700; font-size: 1.2rem; color: #E6EDF3; 
    letter-spacing: -0.5px;
}
.logo-icon {
    background: linear-gradient(135deg, #8A2BE2, #4169E1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.4rem;
}
.navbar-actions { display: flex; gap: 12px; }
.nbtn {
    padding: 8px 16px; border-radius: 6px; font-size: 0.85rem; font-weight: 500;
    cursor: pointer; transition: all 0.2s ease; border: 1px solid transparent;
}
.nbtn-sec { background: transparent; color: #8B949E; border-color: #30363D; }
.nbtn-sec:hover { background: #21262D; color: #C9D1D9; }
.nbtn-pri { background: #8A2BE2; color: #ffffff; }
.nbtn-pri:hover { background: #9333EA; transform: translateY(-1px); }

/* ── WIDGETS Y CONTENEDORES ── */
/* Estilo general para las tarjetas/paneles laterales */
.panel-title {
    font-size: 0.85rem; font-weight: 600; text-transform: uppercase; 
    letter-spacing: 1px; color: #8B949E; margin-bottom: 12px;
    border-bottom: 1px solid #30363D; padding-bottom: 8px; margin-top: 24px;
}

/* File Uploader arreglado (sin texto aplastado) */
div[data-testid="stFileUploader"] {
    background: #161B22 !important;
    border: 1px dashed #30363D !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
}
div[data-testid="stFileUploader"]:hover {
    border-color: #8A2BE2 !important;
}

/* Inputs, Selects, text areas */
div[data-testid="stSelectbox"] > div > div, 
div[data-testid="stTextArea"] textarea {
    background: #0D1117 !important;
    border: 1px solid #30363D !important;
    color: #C9D1D9 !important;
    border-radius: 8px !important;
}
div[data-testid="stSelectbox"] > div > div:focus-within,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #8A2BE2 !important;
    box-shadow: 0 0 0 1px #8A2BE2 !important;
}

/* Botones principales de acción */
.stButton > button {
    background: linear-gradient(135deg, #8A2BE2, #4169E1) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    border: 1px solid #8A2BE2 !important;
    color: #E6EDF3 !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: rgba(138, 43, 226, 0.1) !important;
}

/* ── ELEMENTOS VISUALES ── */
.seg-block {
    background: #161B22; border-radius: 8px; padding: 12px; margin-bottom: 12px;
    border-left: 3px solid #30363D; transition: border-color 0.2s;
}
.seg-block:focus-within { border-left-color: #8A2BE2; }
.seg-time { font-size: 0.75rem; color: #8B949E; margin-bottom: 8px; font-family: monospace; }

.video-placeholder {
    background: #161B22; border: 1px solid #30363D; border-radius: 12px; 
    padding: 60px 20px; text-align: center; margin-top: 24px;
}
.video-placeholder h3 { color: #E6EDF3; font-size: 1.2rem; margin-bottom: 8px; font-weight: 600;}
.video-placeholder p { color: #8B949E; font-size: 0.85rem; }

div[data-testid="stVideo"] video {
    border-radius: 12px;
    border: 1px solid #30363D;
    background: #000;
}

.tips-box {
    background: rgba(48, 54, 61, 0.4); border-radius: 8px; padding: 16px; 
    margin-top: 24px; font-size: 0.85rem; color: #C9D1D9; border: 1px solid #30363D;
}
.tips-box strong { color: #8A2BE2; }

/* Labels de radio buttons y toggles */
div[data-testid="stRadio"] label, div[data-testid="stToggle"] label, div[data-testid="stWidgetLabel"] p {
    color: #C9D1D9 !important;
    font-weight: 500 !important;
}

</style>
""", unsafe_allow_html=True)

# ── Barra de navegación ────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div class="navbar-logo">
    <span class="logo-icon">▶</span>
    TranscribeThat
  </div>
</div>
""", unsafe_allow_html=True)

# ── Helper: chunk de N palabras (CON WORD TIMESTAMPS) ──────────────────────────
def split_segment_into_chunks(seg, max_words=3):
    if "words" in seg and seg["words"]:
        words = seg["words"]
        chunks = []
        idx = 0
        for i in range(0, len(words), max_words):
            chunk_words = words[i:i + max_words]
            text = " ".join([w["word"].strip() for w in chunk_words])
            t_start = chunk_words[0]["start"]
            t_end = chunk_words[-1]["end"]
            chunks.append({"start": t_start, "end": t_end, "text": text, "_idx": idx})
            idx += 1
        return chunks
        
    words = seg["text"].strip().split()
    if not words: return []
    duration = seg["end"] - seg["start"]
    total_words = len(words)
    chunks = []
    idx = 0
    word_pos = 0
    while word_pos < total_words:
        chunk_words = words[word_pos: word_pos + max_words]
        chunk_text = " ".join(chunk_words)
        t_start = seg["start"] + (word_pos / total_words) * duration
        t_end   = seg["start"] + (min(word_pos + max_words, total_words) / total_words) * duration
        chunks.append({"start": t_start, "end": t_end, "text": chunk_text, "_idx": idx})
        word_pos += max_words
        idx += 1
    return chunks

# ── Session state ──────────────────────────────────────────────────────────────
if "segments"     not in st.session_state: st.session_state.segments     = []
if "edited_texts" not in st.session_state: st.session_state.edited_texts = {}
if "video_bytes"  not in st.session_state: st.session_state.video_bytes  = None
if "max_words"    not in st.session_state: st.session_state.max_words    = 3

# ── Layout ajustado (Columnas más anchas a los lados) ──────────────────────────
col_l, col_m, col_r = st.columns([1.3, 2.0, 1.3], gap="large")

# ═══════════════════════ COLUMNA IZQUIERDA ════════════════════════════════════
with col_l:
    st.markdown('<div class="panel-title">Entrada de vídeo</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Sube tu Reel",
        type=["mp4", "mov", "mkv", "avi", "webm"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="panel-title">Motor de IA</div>', unsafe_allow_html=True)
    whisper_model = st.selectbox(
        "Modelo Whisper",
        ["tiny (rápido)", "base (recomendado)", "small (preciso)", "medium (lento)"],
        index=1,
    )
    model_key = whisper_model.split(" ")[0]

    st.markdown('<div class="panel-title">Corte de subtítulos</div>', unsafe_allow_html=True)
    max_words = st.radio(
        "Palabras por bloque",
        [2, 3, 4],
        index=1,
        horizontal=True,
    )
    st.session_state.max_words = max_words

    if uploaded:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚡ Transcribir Audio"):
            with tempfile.NamedTemporaryFile(suffix=Path(uploaded.name).suffix, delete=False) as tmp:
                tmp.write(uploaded.getbuffer())
                tmp_path = tmp.name
            with st.spinner("🧠 Escuchando vídeo (alta precisión)..."):
                model = whisper.load_model(model_key)
                result = model.transcribe(tmp_path, fp16=False, word_timestamps=True)
            
            all_chunks = []
            for seg in result["segments"]:
                all_chunks.extend(split_segment_into_chunks(seg, max_words=st.session_state.max_words))
            st.session_state.segments = all_chunks
            st.session_state.edited_texts = {i: c["text"] for i, c in enumerate(all_chunks)}
            st.session_state.video_bytes = None
            os.unlink(tmp_path)
            st.rerun()

    st.markdown("""
    <div class="tips-box">
        <strong>💡 Tip de creador:</strong><br><br>
        Usa bloques de 2-3 palabras para máxima retención de audiencia en TikTok/Reels.
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════ COLUMNA CENTRAL ══════════════════════════════════════
with col_m:
    if uploaded:
        if st.session_state.video_bytes:
            st.video(st.session_state.video_bytes)
        else:
            st.video(uploaded)
    else:
        st.markdown("""
        <div class="video-placeholder">
            <h3>Área de visualización</h3>
            <p>Sube un archivo de vídeo para comenzar</p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.segments:
        st.markdown('<div class="panel-title">Editor de Transcripción</div>', unsafe_allow_html=True)

        def fmt(t):
            m, s = divmod(int(t), 60)
            return f"{m:02d}:{s:02d}.{int((t % 1) * 10)}"

        for i, seg in enumerate(st.session_state.segments):
            st.markdown(
                f"<div class='seg-block'>"
                f"<div class='seg-time'>⏱ {fmt(seg['start'])} — {fmt(seg['end'])}</div>",
                unsafe_allow_html=True,
            )
            edited = st.text_area(
                f"Seg {i + 1}",
                value=st.session_state.edited_texts.get(i, seg["text"].strip()),
                key=f"t_{i}",
                label_visibility="collapsed",
                height=68,
            )
            st.session_state.edited_texts[i] = edited
            st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════ COLUMNA DERECHA ══════════════════════════════════════
with col_r:
    st.markdown('<div class="panel-title">Estética visual</div>', unsafe_allow_html=True)

    # ── AÑADIDA MONTSERRAT AQUÍ ──
    font_options = {
        "Montserrat (Moderna)": "Montserrat",
        "Sans Serif (Clásica)": "DejaVu Sans",
        "Arial": "Arial",
        "Impact (Llamativa)": "Impact",
        "Helvetica": "Helvetica",
    }
    font_label = st.selectbox("Tipografía", list(font_options.keys()))
    font_name = font_options[font_label]

    font_size = st.slider("Tamaño de texto", 12, 90, 52)
    font_color = st.color_picker("Color principal", "#FFFFFF")

    bg_options = {
        "Transparente (Sin fondo)": None,
        "Caja Negra": "#000000",
        "Caja Violeta": "#8A2BE2",
    }
    bg_label = st.selectbox("Fondo del texto", list(bg_options.keys()))

    st.markdown('<div class="panel-title">Posición y Layout</div>', unsafe_allow_html=True)
    position = st.radio("Posición vertical", ["Arriba", "Centro", "Abajo"], index=2, horizontal=True)
    align = st.radio("Alineación", ["Izquierda", "Centro", "Derecha"], index=1, horizontal=True)

    st.markdown('<div class="panel-title">Efectos</div>', unsafe_allow_html=True)
    col_ef1, col_ef2 = st.columns(2)
    with col_ef1:
        outline_on = st.toggle("Contorno", value=True)
        if outline_on:
            outline_color = st.color_picker("Color contorno", "#000000", label_visibility="collapsed")
        else:
            outline_color = "#000000"
    with col_ef2:
        shadow_on = st.toggle("Sombra paralela", value=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Botón Renderizar ───────────────────────────────────────────────────────
    can_render = uploaded is not None and len(st.session_state.segments) > 0

    if can_render:
        if st.button("🎬 Procesar Vídeo Final"):
            with tempfile.TemporaryDirectory() as tmp:
                ext = Path(uploaded.name).suffix
                in_name = f"input{ext}"
                in_path = os.path.join(tmp, in_name)
                with open(in_path, "wb") as f:
                    f.write(uploaded.getbuffer())

                def hex2ass(hx):
                    h = hx.lstrip("#").upper()
                    if len(h) == 3:
                        h = h[0]*2 + h[1]*2 + h[2]*2
                    r, g, b = h[0:2], h[2:4], h[4:6]
                    return f"&H00{b}{g}{r}"

                def s2ass(t):
                    h = int(t // 3600)
                    m = int((t % 3600) // 60)
                    s = t % 60
                    cs = int((s - int(s)) * 100)
                    return f"{h}:{m:02d}:{int(s):02d}.{cs:02d}"

                fc = hex2ass(font_color)
                oc = hex2ass(outline_color)
                outline_w = 3 if outline_on else 0
                shadow_w  = 2 if shadow_on  else 0

                base_align = {"Izquierda": 0, "Centro": 1, "Derecha": 2}[align]
                if position == "Abajo":    
                    ass_align = 1 + base_align
                    margin_v = 350
                elif position == "Centro": 
                    ass_align = 4 + base_align
                    margin_v = 0
                else:                      
                    ass_align = 7 + base_align
                    margin_v = 350

                ass_path = os.path.join(tmp, "subs.ass")
                ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{fc},&H00FFFFFF,{oc},&H80000000,1,0,0,0,100,100,0,0,1,{outline_w},{shadow_w},{ass_align},40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
                with open(ass_path, "w", encoding="utf-8") as f:
                    f.write(ass_header)
                    for i, seg in enumerate(st.session_state.segments):
                        text = st.session_state.edited_texts.get(i, seg["text"].strip())
                        text = text.replace("{", "\\{").replace("}", "\\}")
                        f.write(
                            f"Dialogue: 0,{s2ass(seg['start'])},{s2ass(seg['end'])},"
                            f"Default,,0,0,0,,{text}\n"
                        )

                filter_path = os.path.join(tmp, "filtro.txt")
                with open(filter_path, "w", encoding="utf-8") as f:
                    f.write("ass=filename=subs.ass")

                uid = uuid.uuid4().hex[:8]
                out_name = f"out_{uid}.mp4"
                out_path = os.path.join(tmp, out_name)

                if os.path.exists("/opt/homebrew/bin/ffmpeg"):
                    ruta_ffmpeg = "/opt/homebrew/bin/ffmpeg"
                elif os.path.exists("/usr/local/bin/ffmpeg"):
                    ruta_ffmpeg = "/usr/local/bin/ffmpeg"
                else:
                    ruta_ffmpeg = "ffmpeg"

                cmd = [
                    ruta_ffmpeg, "-y", "-i", in_name,
                    "-map", "0:v:0", "-map", "0:a:0",
                    "-filter_script:v", "filtro.txt",
                    "-c:v", "libx264", "-crf", "22", "-preset", "fast",
                    "-c:a", "aac", "-movflags", "+faststart",
                    out_name,
                ]
                with st.spinner("Renderizando subtítulos..."):
                    proc = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True)

                if proc.returncode != 0:
                    st.error("Error en FFmpeg:")
                    with st.expander("Ver log de error"):
                        st.code(proc.stderr[-2000:])
                else:
                    with open(out_path, "rb") as f:
                        st.session_state.video_bytes = f.read()
                    st.rerun()

    if st.session_state.video_bytes:
        st.success("✅ ¡Renderizado completo!")
        st.download_button(
            "⬇ Descargar MP4",
            data=st.session_state.video_bytes,
            file_name="reel_subtitulado.mp4",
            mime="video/mp4",
        )label[data-testid="stWidgetLabel"] {
    font-size: 0.78rem !important; font-weight: 500 !important; color: #9ca3af !important;
}
div[data-testid="stFileUploader"] {
    background: #1e2128 !important; border: 2px dashed #2a2d36 !important;
    border-radius: 12px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 0.86rem !important; width: 100% !important;
}
.stButton > button:hover { opacity: 0.88 !important; }
div[data-testid="stDownloadButton"] > button {
    background: #2a2d36 !important; border: 1px solid #3a3d46 !important;
    color: #e8eaf0 !important; border-radius: 8px !important; width: 100% !important;
}
div[data-testid="stVideo"] video { border-radius: 12px; max-height: 440px; }
div[data-testid="stRadio"] label { font-size: 0.82rem !important; color: #9ca3af !important; }
div[data-testid="stToggle"] label { font-size: 0.82rem !important; }
div[data-testid="stAlert"] {
    background: #1e2128 !important; border-left: 3px solid #7c3aed !important; border-radius: 8px !important;
}
div[data-testid="stExpander"] {
    background: #1a1d24 !important; border: 1px solid #2a2d36 !important; border-radius: 10px !important;
}
#MainMenu, footer, header { visibility: hidden; }

.seg-block {
    background: #1e2128; border: 1px solid #2a2d36; border-radius: 8px;
    padding: 10px 12px; margin-bottom: 8px;
}
.seg-block:hover { border-color: #7c3aed44; }
.seg-time { font-size: 0.72rem; font-family: monospace; color: #6b7280; margin-bottom: 4px; }

.tips-box {
    background: #1a1d24; border: 1px solid #2a2d36; border-radius: 10px;
    padding: 14px; margin-top: 12px;
}
.tips-box div { font-size: 0.78rem; color: #6b7280; line-height: 1.9; }
</style>
""", unsafe_allow_html=True)

# ── Navbar ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div class="navbar-logo">
    <div class="logo-dot">▶</div>
    AutoSub AI
  </div>
  <div class="navbar-center">Mi video REEL &nbsp;✎</div>
  <div class="navbar-actions">
    <span class="nbtn nbtn-sec">↩ Deshacer</span>
    <span class="nbtn nbtn-sec">Guardar borrador</span>
    <span class="nbtn nbtn-pri">⬇ Exportar video</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "segments"     not in st.session_state: st.session_state.segments     = []
if "edited_texts" not in st.session_state: st.session_state.edited_texts = {}
if "video_bytes"  not in st.session_state: st.session_state.video_bytes  = None

# ── Layout: 3 columns ─────────────────────────────────────────────────────────
col_l, col_m, col_r = st.columns([1, 2.2, 1.5], gap="medium")

# ═══════════════════════ LEFT COLUMN ══════════════════════════════════════════
with col_l:
    st.markdown("<div style='padding:16px 6px 0 16px'>", unsafe_allow_html=True)

    st.markdown('<div class="sec-label">Archivo de vídeo</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Sube tu Reel",
        type=["mp4", "mov", "mkv", "avi", "webm"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="sec-label">Modelo de IA</div>', unsafe_allow_html=True)
    whisper_model = st.selectbox(
        "Modelo Whisper",
        ["tiny (rápido)", "base (recomendado)", "small (preciso)", "medium (lento)"],
        index=1,
        label_visibility="collapsed",
    )
    model_key = whisper_model.split(" ")[0]

    if uploaded:
        if st.button("⚡  Transcribir audio"):
            with tempfile.NamedTemporaryFile(suffix=Path(uploaded.name).suffix, delete=False) as tmp:
                tmp.write(uploaded.getbuffer())
                tmp_path = tmp.name
            with st.spinner("🧠 Transcribiendo con Whisper…"):
                model = whisper.load_model(model_key)
                # fp16=False evita el warning en CPU
                result = model.transcribe(tmp_path, fp16=False)
            st.session_state.segments = result["segments"]
            st.session_state.edited_texts = {
                i: seg["text"].strip() for i, seg in enumerate(result["segments"])
            }
            st.session_state.video_bytes = None
            os.unlink(tmp_path)
            st.rerun()

    if st.session_state.segments:
        st.markdown("---")
        n = len(st.session_state.segments)
        st.markdown(
            f"<div style='font-size:0.8rem; color:#7c3aed'>✅ {n} segmentos listos</div>",
            unsafe_allow_html=True
        )
        total = st.session_state.segments[-1]["end"]
        st.markdown(
            f"<div style='font-size:0.78rem; color:#6b7280; margin-top:4px'>⏱ Duración: {int(total//60):02d}:{int(total%60):02d}</div>",
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════ CENTER COLUMN ════════════════════════════════════════
with col_m:
    st.markdown("<div style='padding:16px 4px 0'>", unsafe_allow_html=True)

    # Video preview
    if uploaded:
        st.markdown('<div class="sec-label">Vista previa</div>', unsafe_allow_html=True)
        if st.session_state.video_bytes:
            st.video(st.session_state.video_bytes)
        else:
            st.video(uploaded)
    else:
        st.markdown("""
        <div style='background:#1e2128; border:2px dashed #2a2d36; border-radius:16px;
             padding:80px 20px; text-align:center; color:#4b5563; margin-top:12px'>
            <div style='font-size:3rem; margin-bottom:12px'>🎬</div>
            <div style='font-weight:600; color:#6b7280; margin-bottom:6px'>Sube un Reel para empezar</div>
            <div style='font-size:0.82rem'>MP4, MOV, MKV · Formato 9:16 recomendado</div>
        </div>
        """, unsafe_allow_html=True)

    # Transcription editor
    if st.session_state.segments:
        st.markdown("")
        st.markdown("""
        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px'>
            <div class='sec-label' style='margin:0'>Transcripción — edita para corregir errores</div>
        </div>
        """, unsafe_allow_html=True)

        def fmt(t):
            m, s = divmod(int(t), 60)
            return f"{m:02d}:{s:02d}.{int((t%1)*10)}"

        for i, seg in enumerate(st.session_state.segments):
            st.markdown(
                f"<div class='seg-block'>"
                f"<div class='seg-time'>▶ {fmt(seg['start'])} → {fmt(seg['end'])}</div>",
                unsafe_allow_html=True
            )
            edited = st.text_area(
                f"Segmento {i+1}",
                value=st.session_state.edited_texts.get(i, seg["text"].strip()),
                key=f"t_{i}",
                label_visibility="collapsed",
                height=70,
            )
            st.session_state.edited_texts[i] = edited
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════ RIGHT COLUMN ═════════════════════════════════════════
with col_r:
    st.markdown("<div style='padding:16px 16px 0 6px'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.95rem; font-weight:700; color:#e8eaf0; margin-bottom:4px'>"
        "Estilo de subtítulos</div>",
        unsafe_allow_html=True
    )

    # Font
    st.markdown('<div class="sec-label">Fuente</div>', unsafe_allow_html=True)
    font_options = {
        "Poppins Bold (recomendada)": "DejaVu Sans",
        "Arial": "Arial",
        "Impact": "Impact",
        "Helvetica": "Helvetica",
        "Georgia (serif)": "Georgia",
        "Courier New (mono)": "Courier New",
        "Trebuchet MS": "Trebuchet MS",
    }
    font_label = st.selectbox("Fuente", list(font_options.keys()), label_visibility="collapsed")
    font_name = font_options[font_label]

    # Size
    st.markdown('<div class="sec-label">Tamaño</div>', unsafe_allow_html=True)
    font_size = st.slider("Tamaño", 12, 72, 42, label_visibility="collapsed")

    # Text color
    st.markdown('<div class="sec-label">Color del texto</div>', unsafe_allow_html=True)
    font_color = st.color_picker("Color texto", "#FFFFFF", label_visibility="collapsed")

    # Background / box
    st.markdown('<div class="sec-label">Color de fondo del subtítulo</div>', unsafe_allow_html=True)
    bg_options = {
        "Sin fondo": None,
        "Negro semitransparente": "black",
        "Negro sólido": "#000000",
        "Blanco": "#FFFFFF",
        "Morado": "#7c3aed",
    }
    bg_label = st.selectbox("Fondo", list(bg_options.keys()), label_visibility="collapsed")

    # Position
    st.markdown('<div class="sec-label">Posición</div>', unsafe_allow_html=True)
    position = st.radio("Pos", ["Arriba", "Centro", "Abajo"], index=2, horizontal=True, label_visibility="collapsed")
    pos_map = {
        "Abajo":  "(w-text_w)/2:h-th-60",
        "Centro": "(w-text_w)/2:(h-text_h)/2",
        "Arriba": "(w-text_w)/2:60",
    }

    # Alignment
    st.markdown('<div class="sec-label">Alineación</div>', unsafe_allow_html=True)
    align = st.radio("Alin", ["← Izq", "· Centro", "Der →"], index=1, horizontal=True, label_visibility="collapsed")
    align_val = {"← Izq": 1, "· Centro": 2, "Der →": 3}[align]

    # Outline / Shadow
    st.markdown('<div class="sec-label">Efectos</div>', unsafe_allow_html=True)
    col_o, col_s = st.columns(2)
    with col_o:
        outline_on = st.toggle("Contorno", value=True)
        if outline_on:
            outline_color = st.color_picker("Color contorno", "#000000", label_visibility="collapsed")
        else:
            outline_color = "#000000"
    with col_s:
        shadow_on = st.toggle("Sombra", value=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Render ─────────────────────────────────────────────────────────────────
    can_render = uploaded is not None and len(st.session_state.segments) > 0

    if can_render:
        if st.button("🎞️  Renderizar subtítulos"):
            with tempfile.TemporaryDirectory() as tmp:
                in_path = os.path.join(tmp, "input" + Path(uploaded.name).suffix)
                with open(in_path, "wb") as f:
                    f.write(uploaded.getbuffer())

                # Build SRT with edited text
                srt_path = os.path.join(tmp, "subs.srt")

                def s2srt(t):
                    h = int(t // 3600); m = int((t % 3600) // 60)
                    s = int(t % 60);    ms = int((t - int(t)) * 1000)
                    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

                with open(srt_path, "w", encoding="utf-8") as f:
                    for i, seg in enumerate(st.session_state.segments):
                        text = st.session_state.edited_texts.get(i, seg["text"].strip())
                        f.write(f"{i+1}\n{s2srt(seg['start'])} --> {s2srt(seg['end'])}\n{text}\n\n")

                # Color conversion hex → ASS &HBBGGRR
                def hex2ass(hx):
                    h = hx.lstrip("#")
                    r, g, b = h[0:2], h[2:4], h[4:6]
                    return f"&H00{b}{g}{r}"

                fc = hex2ass(font_color)
                oc = hex2ass(outline_color)
                outline_w = 2 if outline_on else 0
                shadow_w  = 1 if shadow_on  else 0

                safe_srt = srt_path.replace("\\", "/")
                # Windows drive-letter colon escape
                if len(safe_srt) > 2 and safe_srt[1] == ":":
                    safe_srt = safe_srt[0] + "\\:" + safe_srt[2:]

                style = (
                    f"FontName={font_name},"
                    f"FontSize={font_size},"
                    f"PrimaryColour={fc},"
                    f"OutlineColour={oc},"
                    f"Outline={outline_w},"
                    f"Shadow={shadow_w},"
                    f"Alignment={align_val},"
                    f"MarginV=50,"
                    f"Bold=1"
                )
                vf = f"subtitles='{safe_srt}':force_style='{style}'"

                out_path = os.path.join(tmp, "out.mp4")
                cmd = [
                    "ffmpeg", "-y", "-i", in_path,
                    "-vf", vf,
                    "-c:v", "libx264", "-crf", "22", "-preset", "fast",
                    "-c:a", "aac",
                    out_path,
                ]
                with st.spinner("🎞️ Renderizando…"):
                    proc = subprocess.run(cmd, capture_output=True, text=True)

                if proc.returncode != 0:
                    st.error("Error en FFmpeg:")
                    with st.expander("Ver log"):
                        st.code(proc.stderr[-2000:])
                else:
                    with open(out_path, "rb") as f:
                        st.session_state.video_bytes = f.read()
                    st.rerun()
    else:
        st.markdown(
            "<div style='background:#1e2128; border-radius:8px; padding:10px 12px; "
            "font-size:0.82rem; color:#4b5563; text-align:center'>"
            "Sube un vídeo y transcríbelo primero</div>",
            unsafe_allow_html=True
        )

    if st.session_state.video_bytes:
        st.success("✅ Listo para descargar")
        st.download_button(
            "⬇️  Descargar MP4 subtitulado",
            data=st.session_state.video_bytes,
            file_name="reel_subtitulado.mp4",
            mime="video/mp4",
        )

    st.markdown("""
    <div class="tips-box">
        <div style='font-size:0.78rem; font-weight:600; color:#9ca3af; margin-bottom:8px'>💡 Consejos</div>
        <div>
            ✎ Edita la transcripción para corregir errores<br>
            ▶ Usa Espacio para reproducir/pausar<br>
            📐 Formato 9:16 ideal para Reels<br>
            🎯 Exporta en alta calidad
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
