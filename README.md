# ⚡ CVForge — Rachit's CV Builder & ATS Checker

A full-featured Django web app to build stunning CVs and check ATS compatibility.

---

## 🚀 Features

- **CV Builder** — 10-step guided form with all sections
- **6 CV Templates** — Modern, Executive, Creative, Tech, Elegant, Bold
- **ATS Score Checker** — AI-powered keyword & compatibility analysis
- **Score Breakdown** — Keywords, Format, Content, Skills Match scores
- **Smart Suggestions** — Personalized tips to improve your score
- **PDF Export** — Print-ready CV via browser Print dialog
- **Sample Job Descriptions** — 4 pre-loaded JD templates
- **Animated UI** — Green/purple theme with particle background

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py migrate
```

### 3. Start the server
```bash
python manage.py runserver
```

### 4. Open in browser
```
http://localhost:8000
```

---

## 🤖 AI-Powered ATS (Free Groq API)

For smarter ATS analysis using LLaMA 3, get a **free** API key:

1. Sign up at https://console.groq.com (free tier, no credit card)
2. Create an API key
3. Set it as environment variable:

```bash
# Linux/Mac
export GROQ_API_KEY="your_key_here"

# Windows
set GROQ_API_KEY=your_key_here
```

Without the key, the app uses a built-in smart keyword analysis algorithm.

---

## 📁 Project Structure

```
cvbuilder/
├── cvbuilder/          # Django project settings
│   ├── settings.py
│   └── urls.py
├── cv_app/             # Main app
│   ├── models.py       # CVProfile & ATSScore models
│   ├── views.py        # All views + ATS logic
│   ├── urls.py
│   └── templates/
│       └── cv_app/
│           ├── base.html       # Animated base layout
│           ├── home.html       # Dashboard
│           ├── builder.html    # 10-step CV builder
│           ├── preview.html    # CV preview (6 templates)
│           ├── ats.html        # ATS checker
│           └── print.html      # Print-ready CV
├── requirements.txt
└── manage.py
```

---

## 🎨 Templates

| Template   | Style                    | Best For            |
|------------|--------------------------|---------------------|
| Modern     | Green/purple gradient    | Tech, Startups      |
| Executive  | Classic serif            | Corporate, Finance  |
| Creative   | Dark, glowing accents    | Design, Media       |
| Tech       | Code-editor style        | Developers          |
| Elegant    | Minimal, centered        | Academia, Law       |
| Bold       | High contrast, dramatic  | Sales, Marketing    |

---

Built with ❤️ for Rachit by CVForge
