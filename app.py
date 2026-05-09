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
        )
