# 🎬 Subtitle that!

App para subtitular vídeos tipo Reel de forma automática con IA (Whisper) y personalización completa de estilo.

## ✨ Funcionalidades

- **Transcripción automática** con OpenAI Whisper (4 modelos: tiny → medium)
- **Subtítulos quemados** en el vídeo con FFmpeg (no como pista separada)
- **Personalización completa**:
  - 🔤 Tipografía (Arial, Impact, Helvetica, Georgia, Courier…)
  - 📏 Tamaño de letra (12–64 px)
  - 🎨 Color del texto y del borde/sombra
  - 📍 Posición (arriba / centro / abajo)
- **Descarga directa** del vídeo subtitulado en MP4

---

## 🚀 Instalación local

### 1. Requisitos previos

- Python 3.9–3.11
- **FFmpeg** instalado en el sistema

#### Instalar FFmpeg:

| Sistema | Comando |
|---------|---------|
| macOS   | `brew install ffmpeg` |
| Ubuntu/Debian | `sudo apt install ffmpeg` |
| Windows | Descarga desde [ffmpeg.org](https://ffmpeg.org/download.html) y añade al PATH |

### 2. Clonar / descargar el proyecto

```bash
# Si tienes git:
git clone <tu-repo>
cd reel-subtitler

# O simplemente copia los archivos app.py y requirements.txt en una carpeta
```

### 3. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# macOS / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

> La primera vez descarga el modelo Whisper (~150 MB para `base`). Necesitas conexión a internet.

### 5. Lanzar la app

```bash
streamlit run app.py
```

Se abrirá automáticamente en `http://localhost:8501`

---

## ☁️ Desplegar en Streamlit Cloud

1. Sube el proyecto a GitHub (repo público o privado).
2. Ve a [share.streamlit.io](https://share.streamlit.io) y conecta tu repo.
3. Asegúrate de incluir un archivo `packages.txt` con:

```
ffmpeg
```

4. Streamlit Cloud instalará FFmpeg automáticamente.

> ⚠️ Streamlit Cloud gratuito tiene límite de RAM (~1 GB). Usa el modelo `tiny` o `base` para vídeos cortos.

---

## 📁 Estructura del proyecto

```
reel-subtitler/
├── app.py            # App principal
├── requirements.txt  # Dependencias Python
├── packages.txt      # Paquetes sistema (para Streamlit Cloud)
└── README.md
```

---

## 💡 Consejos

- Para Reels (9:16), el tamaño óptimo es **1080×1920**
- Modelo recomendado: **`base`** para español, rápido y preciso
- Si el audio tiene mucho ruido, prueba con **`small`** o **`medium`**
- Los subtítulos se *queman* en el vídeo (no se pueden editar luego), ideal para subir directamente a Instagram
