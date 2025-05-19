# 🎬 MovieWeb App

A simple Flask-based web application for managing users and their favorite movies using SQLite and OMDb API.

## ✨ Features

- List all users
- View a user's favorite movies
- Add, update, and delete movies
- Uses OMDb API for real movie data
- Flash messages for feedback
- Custom error pages (404, 500)
- Clean, responsive UI with CSS

## 🛠 Prerequisites

- Python 3.10+
- Flask (`pip install flask`)
- SQLAlchemy (`pip install sqlalchemy`)
- Requests (`pip install requests`)
- python-dotenv (`pip install python-dotenv`)

## 🚀 Setup Instructions

1. Clone or copy this repo
2. Create `.env` from `.env.example` and set your OMDb API key
3. Install dependencies:

pip install -r requirements.txt

4. Seed the database:


python seed.py
Run the app:
bash


1
python app.py
Visit: http://localhost:5000

📝 License
MIT

---

📄 File: `LICENSE`

txt
MIT License

Copyright (c) 2025 Martin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
