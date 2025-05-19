\============================================================
🎬  MovieWeb App – Masterschool Capstone Project
================================================

Welcome to **MovieWeb**, a full‑stack Flask application built as part of my
**Masterschool** software‑engineering program.  The goal is simple: give every
cinephile a beautiful place to curate, rate and share their favourite movies.

## 📦  What’s inside?

* **Flask 3.1**             – lightweight, battle‑tested web framework
* **SQLAlchemy 2.0**        – ORM powering an SQLite backend
* **Tailwind CSS**          – utility‑first styling for rapid UI iteration
* **OMDb API integration**  – fetches posters, genres & ratings on the fly
* **Modular architecture**  – clean separation of views, data layer and models

## ✨  Key Features

1. **User Profiles** – create unlimited users, each with a personal watch‑list.
2. **Smart Search**  – type a title, pull real data from the OMDb API in seconds.
3. **CRUD Movies**   – add, edit or delete films; posters zoom on hover.
4. **Flash Feedback**– instant success & error messages (no page reload needed).
5. **Responsive UI** – gradient headers, card layouts & dark overlays for posters.

## 🚀  Quick‑start

```bash
# 1) Clone and enter
$ git clone https://github.com/yourusername/movieweb.git
$ cd movieweb

# 2) Create/activate a virtual env (optional but recommended)
$ python -m venv .venv && source .venv/bin/activate

# 3) Install requirements
$ pip install -r requirements.txt

# 4) Set environment variables
$ cp .env.example .env
# → add your OMDb API key + SECRET_KEY in the .env file

# 5) Seed the database with sample data
$ python seed.py

# 6) Fire up the dev server 🎉
$ python app.py  # then visit http://localhost:5000
```

## 🗄️  Project Structure

```
├─ app.py                 # Flask entry‑point / routes
├─ datamanager/           # ORM models + SQLiteDataManager
│  ├─ models.py
│  ├─ sqlite_data_manager.py
│  └─ data_manager_interface.py
├─ templates/             # Jinja2 + Tailwind markup
├─ static/                # Custom CSS (flash messages)
├─ seed.py                # Demo DB seeding script
├─ requirements.txt       # Python dependencies
└─ LICENSE                # MIT license text
```



© 2025 kaiser-data • Released under the MIT License
