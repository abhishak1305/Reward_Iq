# ⚡ RewardIQ — AI-Powered Employee Reward System

> A production-ready, full-stack SaaS HR platform built with **React (Vite) + FastAPI**, featuring AI-driven reward recommendations, sentiment analysis, productivity prediction, and real-time analytics.

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8, Vanilla CSS, Recharts |
| Backend | FastAPI, Python 3.12, Pydantic v2, SQLAlchemy (async) |
| Database | PostgreSQL via Neon (asyncpg driver) |
| Auth | JWT (HS256), bcrypt, role-based access control |
| AI/ML | VADER + TextBlob (sentiment), RandomForest (productivity), rule-based recommender, fairness detection |
| Deployment | Vercel (frontend + backend serverless), Neon PostgreSQL |

---

## 📁 Project Structure

```
HRM/
├── frontend/           # React 19 + Vite App
│   └── src/
│       ├── components/ # Reusable UI components
│       ├── lib/        # API utilities
│       ├── pages/      # Route pages
│       └── App.jsx     # Main entry point
├── backend/            # FastAPI App
│   ├── api/v1/         # Route handlers (10 routers)
│   ├── core/           # Config, DB, Security
│   ├── models/         # SQLAlchemy ORM (8 tables)
│   ├── schemas/        # Pydantic v2 schemas
│   ├── ai/             # AI modules (5 modules)
│   ├── tests/          # Pytest test suite
│   └── main.py
├── vercel.json
├── backend/.env.example
└── README.md
```

---

## ⚡ Quick Start (Local Development)

### Prerequisites
- Python 3.12+
- Node.js 20+
- (Optional) PostgreSQL or Neon account — SQLite is used by default for local dev

### 1. Clone & Setup

```bash
git clone <your-repo>
cd HRM
cp backend/.env.example backend/.env
# Edit backend/.env with your actual values
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Download NLTK data for TextBlob
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

# Seed the database with demo data
cd ..
python -m backend.seed

# Start backend
uvicorn backend.main:app --reload --port 8000
```

Backend runs at: http://localhost:8000
API Docs: http://localhost:8000/api/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies using npm (enforces package-lock.json policy)
npm install

# Start dev server
npm run dev
```

Frontend runs at: http://localhost:5173

---



## 🌐 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/auth/register | Register new user |
| POST | /api/v1/auth/login | Login |
| POST | /api/v1/auth/refresh | Refresh token |
| GET | /api/v1/auth/me | Get current user |

### Employees
| Method | Endpoint | Description |
|---|---|---|
| GET | /api/v1/employees | List all (admin) |
| GET | /api/v1/employees/me | My profile |
| GET | /api/v1/employees/ranking | Top performers |
| POST | /api/v1/employees | Create employee |
| PATCH | /api/v1/employees/{id} | Update employee |

### Attendance, Rewards, Bonuses, Feedback
All follow RESTful patterns under `/api/v1/attendance`, `/api/v1/rewards`, `/api/v1/bonuses`, `/api/v1/feedback`

### Analytics
- `GET /api/v1/analytics/overview`
- `GET /api/v1/analytics/department-performance`
- `GET /api/v1/analytics/attendance-trend`
- `GET /api/v1/analytics/reward-distribution`

### AI
- `GET /api/v1/ai/predict/productivity/{id}` — Productivity ML prediction
- `GET /api/v1/ai/recommend/rewards/{id}` — Reward recommendations
- `GET /api/v1/ai/insights/{id}` — Employee AI insight report
- `GET /api/v1/ai/fairness` — Org-wide bias/fairness report
- `GET /api/v1/ai/sentiment/org` — Organisation sentiment summary

---

## 🤖 AI Modules

| Module | Algorithm | Purpose |
|---|---|---|
| `sentiment.py` | VADER + TextBlob ensemble | Score feedback -1 to 1 |
| `predictor.py` | RandomForest Regressor | Predict productivity score |
| `recommender.py` | Rule-based + novelty scoring | Top-K reward recommendations |
| `fairness.py` | Statistical Parity Difference | Detect reward bias by dept |
| `insights.py` | Rule-based profiling | Human-readable insights |

---

## 🗄️ Database Schema

```sql
users(id, email, password_hash, role, is_active, created_at)
employees(id, user_id, full_name, department, position, hire_date, reward_points, productivity_score)
attendance(id, employee_id, date, check_in, check_out, status)
rewards(id, employee_id, awarded_by, reward_type, points, title)
bonuses(id, employee_id, amount, reason, status, approved_by)
feedback(id, employee_id, content, sentiment_score, sentiment_label)
ai_predictions(id, employee_id, prediction_type, score, metadata)
notifications(id, user_id, title, message, is_read)
```

---

## 🚢 Deployment (Vercel + Neon)

### 1. Create Neon Database
1. Go to [neon.tech](https://neon.tech) → Create project
2. Copy the connection string (asyncpg format)

### 2. Deploy to Vercel

```bash
npm install -g vercel

# From project root
vercel --prod
```

### 3. Set Environment Variables in Vercel Dashboard

```
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/rewardiq?sslmode=require
JWT_SECRET_KEY=<your-random-secret>
ENVIRONMENT=production
VITE_API_URL=https://your-app.vercel.app/api/v1
```

### 4. Run migrations in production

```bash
# After deployment, seed prod DB:
DATABASE_URL=<prod-url> python -m backend.seed
```

---

## 🧪 Testing

```bash
# Run from the project root
python -m pytest backend/tests/ -v

# Health check
curl http://localhost:8000/api/health
```

---

## 📊 Features At a Glance

### Employee Dashboard
- 📈 Productivity score + trend
- 📅 Attendance rate + history
- 🏆 Rewards + badges
- 🤖 AI-generated performance insights
- 🎁 Personalised reward recommendations
- 📉 Radar performance chart
- 🔔 In-app notifications

### Admin Dashboard
- 👥 Employee management table
- 📊 Department performance analytics
- 🏅 Live employee rankings
- ✅ Bonus approval workflow
- 🤖 Organisation fairness report
- 💬 Sentiment trend analysis
- 🗂️ Reward distribution charts

---

## 🔒 Security

- JWT with access + refresh token rotation
- bcrypt password hashing (cost factor 12)
- Role-based middleware on every protected route
- CORS configured to allowlist only your domains
- NullPool used with Neon to prevent connection leaks in serverless

---

*Built with ❤️ by RewardIQ*
