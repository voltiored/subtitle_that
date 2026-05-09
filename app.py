import streamlit as st
import whisper
import tempfile
import os
import subprocess
import json
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Reel Subtitler",
    page_icon="🎬",
    layout="centered",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}
.stApp {
    background: #0d0d0d;
    color: #f0f0f0;
}
section[data-testid="stSidebar"] {
    background: #111 !important;
}
.block-container {
    padding-top: 2rem;
    max-width: 720px;
}
.stButton > button {
    background: linear-gradient(135deg, #ff3cac, #784ba0, #2b86c5);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 2rem;
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    width: 100%;
    cursor: pointer;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

.upload-hint {
    border: 2px dashed #444;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    color: #888;
    margin-bottom: 1rem;
}
.preview-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #888;
    margin-bottom: 0.4rem;
}
.status-box {
    background: #1a1a1a;
    border-left: 3px solid #ff3cac;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    font-size: 0.9rem;
    color: #ccc;
}
hr { border-color: #222; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# 🎬 Reel Subtitler")
st.markdown("Transcribe y subtitula tus Reels automáticamente con IA.")
st.markdown("---")

# ── Sidebar: subtitle style options ───────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎨 Estilo de subtítulos")

    font_options = {
        "Arial (limpio)": "Arial",
        "Impact (bold clásico)": "Impact",
        "Helvetica": "Helvetica",
        "Futura / Trebuchet": "Trebuchet MS",
        "Georgia (serif)": "Georgia",
        "Courier (monoespaciado)": "Courier New",
    }
    font_label = st.selectbox("Tipografía", list(font_options.keys()))
    font_name = font_options[font_label]

    font_size = st.slider("Tamaño de letra", min_value=12, max_value=64, value=28, step=2)

    font_color = st.color_picker("Color del texto", "#FFFFFF")
    border_color = st.color_picker("Color del borde / sombra", "#000000")

    position = st.selectbox(
        "Posición",
        ["Abajo (centro)", "Centro", "Arriba (centro)"],
        index=0,
    )
    pos_map = {
        "Abajo (centro)": "(w-text_w)/2:h-th-40",
        "Centro":         "(w-text_w)/2:(h-text_h)/2",
        "Arriba (centro)": "(w-text_w)/2:40",
    }
    subtitle_position = pos_map[position]

    whisper_model = st.selectbox(
        "Modelo Whisper (precisión vs velocidad)",
        ["tiny", "base", "small", "medium"],
        index=1,
        help="'base' es un buen equilibrio. 'medium' es más preciso pero más lento.",
    )

    st.markdown("---")
    st.markdown(
        "<small style='color:#555'>Powered by OpenAI Whisper + FFmpeg</small>",
        unsafe_allow_html=True,
    )

# ── File upload ────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Sube tu vídeo (MP4, MOV, MKV…)",
    type=["mp4", "mov", "mkv", "avi", "webm"],
    help="Recomendado: formato vertical 9:16 para Reels",
)

if uploaded:
    st.markdown('<p class="preview-label">Vista previa del original</p>', unsafe_allow_html=True)
    st.video(uploaded)

    st.markdown("---")

    # ── Action button ──────────────────────────────────────────────────────────
    if st.button("⚡  Transcribir y añadir subtítulos"):

        with tempfile.TemporaryDirectory() as tmp:
            # Save upload
            in_path = os.path.join(tmp, "input" + Path(uploaded.name).suffix)
            with open(in_path, "wb") as f:
                f.write(uploaded.getbuffer())

            # ── Step 1: Transcribe with Whisper ────────────────────────────────
            with st.spinner("🧠 Transcribiendo audio con Whisper…"):
                model = whisper.load_model(whisper_model)
                result = model.transcribe(in_path, word_timestamps=False)

            segments = result["segments"]

            if not segments:
                st.error("No se detectó audio o la transcripción está vacía.")
                st.stop()

            # Show transcript
            with st.expander("📝 Transcripción completa", expanded=False):
                for seg in segments:
                    st.write(f"[{seg['start']:.1f}s → {seg['end']:.1f}s] {seg['text'].strip()}")

            # ── Step 2: Build SRT ──────────────────────────────────────────────
            srt_path = os.path.join(tmp, "subs.srt")

            def seconds_to_srt(t):
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = int(t % 60)
                ms = int((t - int(t)) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

            with open(srt_path, "w", encoding="utf-8") as f:
                for i, seg in enumerate(segments, 1):
                    f.write(f"{i}\n")
                    f.write(f"{seconds_to_srt(seg['start'])} --> {seconds_to_srt(seg['end'])}\n")
                    f.write(seg["text"].strip() + "\n\n")

            # ── Step 3: Burn subtitles with FFmpeg ─────────────────────────────
            out_path = os.path.join(tmp, "output_subtitled.mp4")

            # Convert hex color to FFmpeg format &HBBGGRR (ASS)
            def hex_to_ass(hex_color):
                h = hex_color.lstrip("#")
                r, g, b = h[0:2], h[2:4], h[4:6]
                return f"&H00{b}{g}{r}"

            fc = hex_to_ass(font_color)
            bc = hex_to_ass(border_color)

            # Escape path for FFmpeg filter
            safe_srt = srt_path.replace("\\", "/").replace(":", "\\:")

            subtitles_filter = (
                f"subtitles='{safe_srt}'"
                f":force_style='FontName={font_name},"
                f"FontSize={font_size},"
                f"PrimaryColour={fc},"
                f"OutlineColour={bc},"
                f"Outline=2,"
                f"Shadow=1,"
                f"Alignment=2,"
                f"MarginV=40,"
                f"Bold=1'"
            )

            cmd = [
                "ffmpeg", "-y",
                "-i", in_path,
                "-vf", subtitles_filter,
                "-c:v", "libx264",
                "-crf", "23",
                "-preset", "fast",
                "-c:a", "aac",
                out_path,
            ]

            with st.spinner("🎞️ Renderizando vídeo con subtítulos…"):
                proc = subprocess.run(cmd, capture_output=True, text=True)

            if proc.returncode != 0:
                st.error("Error en FFmpeg:")
                st.code(proc.stderr[-3000:])
                st.stop()

            # ── Step 4: Offer download ─────────────────────────────────────────
            with open(out_path, "rb") as f:
                video_bytes = f.read()

        st.success("✅ ¡Vídeo subtitulado listo!")

        st.markdown('<p class="preview-label">Vista previa con subtítulos</p>', unsafe_allow_html=True)
        st.video(video_bytes)

        st.download_button(
            label="⬇️  Descargar vídeo subtitulado",
            data=video_bytes,
            file_name="reel_subtitulado.mp4",
            mime="video/mp4",
            use_container_width=True,
        )

else:
    st.markdown(
        '<div class="upload-hint">📱 Arrastra aquí tu Reel (MP4, MOV…)<br><small>Formato recomendado: 1080×1920 vertical</small></div>',
        unsafe_allow_html=True,
    )
