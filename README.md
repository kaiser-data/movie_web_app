
# 🎬 MovieWeb App

A full-stack **Flask + SQLite + OMDb** demo built at **Masterschool**.  
Manage users, search real movies via the OMDb API, and curate personal watch-lists — all in a single-page friendly UI styled with Tailwind CSS.

---

## ✨ Key Features

| Area            | What you get                                                        |
|-----------------|---------------------------------------------------------------------|
| **Users**       | Add / list / delete users; auto-increment IDs                       |
| **Movies**      | Search OMDb, auto-fetch posters, store genre/rating/year locally    |
| **Favorites**   | Each user keeps a personal movie shelf (many-to-many)              |
| **UX niceties** | Gradient hero banners, responsive cards, flash toasts, 404 & 500    |
| **Dev goodies** | `seed.py` for demo data, `.env.example`, rich logging, PEP-rated docs |

---
## 🚀 Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/yourname/movieweb.git
cd movieweb

# 2. Create virtual-env
python -m venv .venv && source .venv/bin/activate

# 3. Install deps
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env            # add your OMDB_API_KEY + SECRET_KEY

# 5. Seed demo DB (5 users, 25 movies)
python seed.py

# 6. Launch dev server
python app.py

# open http://localhost:5000
````

---


## 📂 Project Structure

```

movieweb/
├── app.py                     # Flask app entry-point (routes + factory wiring)
├── .env.example               # Sample env vars (OMDB\_API\_KEY, SECRET\_KEY)
├── seed.py                    # Drops/creates tables, injects demo data
├── requirements.txt           # Pip-freeze of runtime deps
│
├── datamanager/               # Data-access layer (flat, no circular deps)
│   ├── **init**.py            # Re-exports SQLiteDataManager & interface
│   ├── data\_manager\_interface.py  # ABC every data backend must implement
│   ├── data\_manager.py        # Simple in-memory fallback (for unit tests)
│   ├── sqlite\_data\_manager.py # Production backend (SQLAlchemy + SQLite)
│   └── models.py              # Declarative ORM models + association table
│
├── templates/                 # Jinja2 views (Tailwind utility classes)
│   ├── base.html              # Global layout (nav, footer, flash include)
│   ├── home.html              # Landing page hero
│   ├── users.html             # Grid of user cards
│   ├── user\_movies.html       # Poster cards & actions
│   ├── add\_user.html          # Form page
│   ├── add\_movie.html         # Search page
│   ├── update\_movie.html      # Edit form
│   ├── 404.html               # Not-found page
│   └── 500.html               # Error page
│
├── static/
│   └── styles.css             # Flash-message colours & close-button JS
│
├── data/                      # SQLite file lives here at runtime
│   └── movies.sqlite          # (auto-generated; ignored by .gitignore)
│

```




## ⚙️ Environment Variables

| Var            | Purpose                                                    |
| -------------- | ---------------------------------------------------------- |
| `OMDB_API_KEY` | Get yours free at [http://omdbapi.com](http://omdbapi.com) |
| `SECRET_KEY`   | Flask session & CSRF protection                            |

---

## 🛠️ Scripts

| Command               | What it does                        |
| --------------------- | ----------------------------------- |
| `python seed.py`      | Resets DB, adds 5 users & 25 movies |
| `python app.py`       | Runs dev server on **:5000**        |
| `pytest` *(optional)* | Unit tests (coming soon)            |

---

## 🧑‍💻 Contributing

1. Fork → feature branch → PR
2. Follow [PEP 8](https://peps.python.org/pep-0008/) & conventional-commit messages
3. Run `black .` before pushing

---

## 📜 License

Released under the MIT License – see [`LICENSE`](LICENSE) for full text.

