import streamlit as st
import whisper
import tempfile
import os
import subprocess
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AutoSub AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: #111318 !important;
    color: #e8eaf0 !important;
}
[data-testid="collapsedControl"], section[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

.navbar {
    display: flex; align-items: center; justify-content: space-between;
    background: #1a1d24; border-bottom: 1px solid #2a2d36;
    padding: 0 24px; height: 56px;
}
.navbar-logo { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 1rem; color: #fff; }
.logo-dot {
    width: 28px; height: 28px; background: linear-gradient(135deg, #7c3aed, #a855f7);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; color: white;
}
.navbar-center { font-size: 0.88rem; color: #9ca3af; }
.navbar-actions { display: flex; gap: 10px; align-items: center; }
.nbtn { padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 500; cursor: pointer; }
.nbtn-sec { background: #2a2d36; color: #e8eaf0; border: none; }
.nbtn-pri { background: linear-gradient(135deg, #7c3aed, #a855f7); color: white; border: none; font-weight: 600; }

.sec-label {
    font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; color: #6b7280; margin: 16px 0 6px;
}

/* Streamlit widget overrides */
div[data-testid="stSelectbox"] > div > div {
    background: #2a2d36 !important; border: 1px solid #3a3d46 !important;
    border-radius: 8px !important; color: #e8eaf0 !important;
}
div[data-testid="stTextArea"] textarea {
    background: #1e2128 !important; border: 1px solid #2a2d36 !important;
    border-radius: 8px !important; color: #e8eaf0 !important;
    font-size: 0.86rem !important; line-height: 1.5 !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.2) !important;
}
label[data-testid="stWidgetLabel"] {
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
