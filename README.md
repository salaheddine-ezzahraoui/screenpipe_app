# Screenpipe - Modern SaaS Dashboard

A modern screen recording dashboard with AI assistant. Built with Flask.

## Quick Start

```bash
# Clone
git clone https://github.com/salaheddine-ezzahraoui/screenpipe_app.git
cd screenpipe_app

# Install
pip install flask requests

# Run
python3 app.py
```

Open **http://localhost:1112**

## Features

- 🎬 Screen Recording Control
- 📹 Video Library
- 🤖 AI Assistant (powered by Phi3)
- ⚙️ Settings
- 📚 Documentation

## Deployment

### Option 1: Render (Free)
1. Push to GitHub
2. Go to [render.com](https://render.com)
3. Create new Web Service
4. Connect your GitHub repo
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn app:app`

### Option 2: Railway
1. Push to GitHub
2. Go to [railway.app](https://railway.app)
3. Create new project from GitHub
4. Deploy automatically

### Option 3: Docker
```bash
docker build -t screenpipe .
docker run -p 1112:1112 screenpipe
```

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML/CSS/JS
- **Icons**: Lucide
- **AI**: Ollama (Phi3)

## About

Created by **Salaheddine Ezzahraoui**
- Email: salaheddine.ezzahraoui1@gmail.com
- GitHub: github.com/salaheddine-ezzahraoui
