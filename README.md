# Alwrity AI Paragraph Rewriter 📝

Rewrite and enhance paragraphs using AI for clarity, tone, and engagement.

---

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the App](#running-the-app)
- [How to Use](#how-to-use)
- [Privacy & Security](#privacy--security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Introduction

**Alwrity AI Paragraph Rewriter** is a user-friendly web tool powered by Google Gemini 2.5 Pro. It allows anyone to rewrite, improve, and rephrase paragraphs in various tones and styles—perfect for writers, students, marketers, and professionals seeking clearer, more engaging text.

---

## Features

- ✍️ One‑click paragraph rewriting (Gemini 2.5 Pro)
- 🎛️ Controls under the textarea (compact, user‑friendly):
  - Mode: Strict (preserve meaning) or Creative (more freedom)
  - Style/Tone: Clear and Engaging, Formal, Casual, Concise, Friendly, Persuasive, Professional
  - Language: English, Spanish, French, German, Hindi, plus Custom
- 🧠 Meaning check with semantic similarity (warns on drift)
- 🔊 Listen/Pause the result (instant playback)
  - Robust long‑text audio via segmented TTS (AssemblyAI) with queued playback
  - Fallback to browser speech synthesis when needed
- 📋 Copy text button with clipboard fallback (works in iframes)
- ⏳ Spinner stays visible until results are fully ready
- 🔢 Live word counter (0/700) and button disabled until input
- 🧼 Streamlined UI: no sidebar, no in‑app feedback form
- 🌙 Dark theme via `.streamlit/config.toml`

---

## Getting Started

### Prerequisites

- Python 3.8 or higher  
- Google Gemini API key ([get one](https://ai.google.dev/))
- AssemblyAI API key for TTS ([sign up](https://www.assemblyai.com/))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/uniqueumesh/alwrity-ai-paragraph-rewriter.git
   cd alwrity-ai-paragraph-rewriter
   ```

2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

1) Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_key
ASSEMBLYAI_API_KEY=your_assemblyai_key
```

2) Start the Streamlit app:
```bash
streamlit run app.py
```
Open the provided local URL in your browser.

---

## How to Use

1. Paste your paragraph (up to 700 words) in the big textbox.  
   - The button enables automatically once you type.
2. Set the dropdowns under the textbox:
   - Mode (Strict/Creative), Tone, and Language (or Custom).
3. Click "Rewrite Paragraph"; the spinner stays until it’s ready.
4. Read the result below. Use Listen/Pause to hear it, or Copy text to copy.
5. Adjust Mode/Tone/Language and click Rewrite again to try variants.

---

## Privacy & Security

- Keys are provided via `.env` locally or Streamlit Secrets in deployment.  
- Text is sent to Gemini for rewriting and to AssemblyAI for audio (when listening).
- The app does not persist your inputs or outputs.

---

## Troubleshooting

- Gemini API errors:
  - Ensure your GEMINI_API_KEY is valid and the input < 700 words.
  - Network issues can cause timeouts; retry or check connectivity.
- Audio stops early in embedded pages:
  - We pre-generate segmented MP3s and queue them for long texts.  
  - Ensure your iframe allows autoplay: `allow="autoplay; clipboard-read; clipboard-write"`.
- Copy text doesn’t work in embed:
  - The button falls back to a textarea copy method. Ensure HTTPS and iframe permissions: `allow="clipboard-read; clipboard-write"`.
- Warnings in terminal:
  - Transformers/Torch FutureWarnings are suppressed at startup for a clean log.

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the MIT License.

---

## Contact

- [Alwrity Website](https://alwrity.com)
- [GitHub Issues](https://github.com/uniqueumesh/alwrity-ai-paragraph-rewriter/issues)

---

### Deployment Notes

- Add secrets on Streamlit Cloud (or your host):
  - `GEMINI_API_KEY`
  - `ASSEMBLYAI_API_KEY`
- The UI uses a dark theme via `.streamlit/config.toml`.

---
