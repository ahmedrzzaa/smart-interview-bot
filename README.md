# 🤖 Smart Interview Bot – CV & Job Description Based Interviewer

This project is an AI-powered interview simulator built with **Streamlit** and **OpenAI GPT-4o**, which generates tailored interview questions based on your uploaded **CV** and a given **Job Description (JD)**. It evaluates your responses and gives **final, consolidated feedback** with a performance score.

---

## 🚀 Features

- Upload CV in `.pdf`, `.docx`, `.txt`, or image formats (`.png`, `.jpg`)
- Enter a Job Description to generate relevant HR + technical interview questions
- Answer each question interactively
- At the end, receive:
  - Your complete Q&A history
  - A single feedback paragraph
  - A final interview score out of 10

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) — Web framework
- [OpenAI GPT-4o](https://platform.openai.com/docs/models/gpt-4o) — Interview generation + evaluation
- [PyMuPDF](https://pymupdf.readthedocs.io/) — For reading PDF CVs
- [python-docx](https://python-docx.readthedocs.io/) — For DOCX file handling
- [EasyOCR](https://www.jaided.ai/easyocr/) — OCR for image-based CVs

---

## ⚙️ Setup Instructions

### 1. Clone this repository

```bash
git clone https://github.com/ahmedrzzaa/smart-interview-bot.git
cd smart-interview-bot
```

### 2. Create and activate virtual environment
```bash
# Windows

python -m venv venv
venv\Scripts\activate
```

### 3. Instal dependencies
```bash
pip install -r requirements.txt
```

### 4. Add Your Key
```bash
from openai import OpenAI
client = OpenAI(api_key="your-api-key-here")
```

### 5. Run App
```bash
streamlit run chatbot.py

