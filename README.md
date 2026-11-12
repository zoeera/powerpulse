# PowerPulse India — Smart Electricity & Solar Savings App

PowerPulse helps Indian households scan paper or PDF electricity bills (including **TGSPDCL**, **UPPCL**, **MPWZ**, and **BSES Delhi**), track appliance usage, spot unexpected bill jumps, estimate future bills, calculate **PM Surya Ghar** rooftop solar savings, and export PDF summaries.

---

## Deploying to Render from GitHub

1. Push this repository to GitHub.
2. Sign in to [Render.com](https://render.com) with your GitHub account.
3. **Deploy Backend (`powerpulse-api`):**
   - Click **New → Web Service** and choose this repository.
   - Set **Root Directory** to `backend` and **Language / Runtime** to **Docker**.
   - Deploy and copy the live backend URL (for example, `https://powerpulse-api.onrender.com`).
   - *(Optional)* Add a free PostgreSQL URL (from Neon, Supabase, or Render Postgres) as `DATABASE_URL` in **Environment** if you want uploaded bills to stay saved across container restarts.
4. **Deploy Frontend (`powerpulse-web`):**
   - Click **New → Static Site** and choose the same repository.
   - Set **Root Directory** to `frontend`.
   - Set **Build Command** to `npm install && npm run build`.
   - Set **Publish Directory** to `dist`.
   - Add Environment Variable `VITE_API_URL` = `https://<your-backend-url>.onrender.com/api/v1`.
   - Deploy and share the live static site URL!

*(Tip: You can also click **New → Blueprint** in Render using the included `render.yaml` file and paste your backend `/api/v1` URL when prompted for `VITE_API_URL`.)*

---

## Running Locally

### Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate  |  macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`.
