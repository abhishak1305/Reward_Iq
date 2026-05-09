# RewardIQ Deployment Guide (Render)

This guide provides step-by-step instructions for deploying the RewardIQ HRM platform on **Render**.

## 1. Project Structure
The repository is structured with a root directory containing both `frontend/` and `backend/`. This is handled automatically by the included `render.yaml`.

## 2. Environment Variables

### Backend (Web Service)
| Variable | Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Enables production optimizations. |
| `DATABASE_URL` | `sqlite+aiosqlite:////data/rewardiq.db` | Path to persistent SQLite DB. |
| `JWT_SECRET_KEY` | *[Auto-generated]* | Secret key for JWT tokens. |
| `OPENROUTER_API_KEY` | `your_api_key` | Required for AI Coach functionality. |
| `ALLOWED_ORIGINS` | `["https://your-frontend.onrender.com"]` | CORS policy for the frontend. |

### Frontend (Static Site)
| Variable | Value | Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `https://your-backend.onrender.com/api/v1` | URL of the deployed backend. |

## 3. Manual Setup Steps on Render

### Step 1: Create a Blueprint
1. Go to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository: `abhishak1305/Reward_Iq`.
4. Render will detect the `render.yaml` and prompt you to create the services.

### Step 2: Persistent Disk (CRITICAL for SQLite)
Since SQLite is a file-based database, it will be lost every time the server restarts unless you use a persistent disk.
1. In the **rewardiq-backend** service settings, go to **Disks**.
2. Click **Add Disk**.
3. **Name:** `rewardiq-data`
4. **Mount Path:** `/data`
5. **Size:** 1GB (Free tier is usually enough).
6. **Update Code:** Ensure your `DATABASE_URL` in environment variables is set to `sqlite+aiosqlite:////data/rewardiq.db`.

### Step 3: Initial Seeding
To populate the database with the initial 20 employees and feedback:
1. Go to the **rewardiq-backend** service.
2. Select **Shell** from the sidebar.
3. Run the following command:
   ```bash
   PYTHONPATH=. python backend/seed.py
   ```

## 4. Build & Start Commands (Handled by render.yaml)
- **Backend Build:** `pip install -r backend/requirements.txt`
- **Backend Start:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Frontend Build:** `cd frontend && npm install && npm run build`
- **Frontend Publish:** `frontend/dist`

## 5. Potential Issues & Fixes
- **CORS Error:** Ensure the `ALLOWED_ORIGINS` in backend env vars exactly matches your frontend URL (including `https://`).
- **Database Locked:** This can happen if multiple processes try to write to SQLite. Render usually runs a single instance, but ensure you aren't running multiple worker processes.
- **Port Binding:** Ensure the backend is listening on `0.0.0.0` and the `$PORT` environment variable provided by Render.
