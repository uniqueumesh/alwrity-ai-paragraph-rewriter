# Alwrity AI Paragraph Rewriter 📝

Rewrite and enhance paragraphs using AI for clarity, tone, and engagement.

---

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Demo](#demo)
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

- ✍️ Rewrite any paragraph with a single click  
- 🎨 Choose from multiple writing styles (e.g., Formal, Concise, Friendly)  
- 🔑 Secure: Your Gemini API key is never stored  
- 🚀 Fast, modern Streamlit web interface  
- 🛡️ Enforces Gemini LLM input limits for reliability  
- 🔄 Always generates a unique rewrite, even for repeated inputs  
- 🖥️ No coding required!

---

## Demo

![Alwrity Paragraph Rewriter Screenshot](assets/demo.png)  
*Screenshot: Simple, modern UI for rewriting paragraphs with style selection.*

---

## Getting Started

### Prerequisites

- Python 3.8 or higher  
- A Google Gemini API key ([get one here](https://ai.google.dev/))

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

Start the Streamlit app:
```bash
streamlit run app.py
```
Open the provided local URL in your browser.

---

## How to Use

1. **Enter your Gemini API key** in the sidebar.  
   - Your key is only used for your session and never stored.
2. **Paste your paragraph** (up to 700 words) in the main input box.
3. **Choose a rewriting style/tone** from the dropdown.
4. **Click "Rewrite Paragraph"**.
5. **View your rewritten paragraph** in the output box.
6. **Repeat or try different styles** until satisfied!

---

## Privacy & Security

- **Your API key is never saved:** It is used only for your session and is erased when the app closes.
- **Your text is processed securely:** Only sent to Google Gemini for rewriting.
- **No data is stored or shared** by this tool.

---

## Troubleshooting

- **Gemini API errors:**  
  - Ensure your API key is correct and has access to Gemini 2.5 Pro.
  - Check your internet connection.
  - Input must be under 700 words.
- **No rewrite or repeated output:**  
  - Try clicking "Rewrite Paragraph" again for a new result.
  - If the problem persists, check your API usage or try a different style.

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
