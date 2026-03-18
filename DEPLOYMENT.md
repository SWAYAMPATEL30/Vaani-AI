# 🚀 Deployment Guide

## Render.com (Recommended for Free Tier)

### Step 1: Prepare Repository
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo>
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: voice-calling-agent
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

### Step 3: Add Environment Variables
In Render dashboard → Environment:
- `ASSEMBLYAI_API_KEY`
- `OPENAI_API_KEY`
- `ELEVENLABS_API_KEY` (or Google TTS credentials)
- `DATABASE_URL` (if using PostgreSQL)
- `WEBHOOK_BASE_URL` (your Render URL)

### Step 4: Get Your URL
Render will provide: `https://your-app.onrender.com`

Update your telephony provider webhooks to use this URL!

---

## Railway.app

### Step 1: Install Railway CLI
```bash
npm i -g @railway/cli
railway login
```

### Step 2: Deploy
```bash
railway init
railway up
```

### Step 3: Add Environment Variables
```bash
railway variables set ASSEMBLYAI_API_KEY=your-key
railway variables set OPENAI_API_KEY=your-key
# ... etc
```

Or use Railway dashboard → Variables tab

---

## Vercel (For API)

### Step 1: Install Vercel CLI
```bash
npm i -g vercel
```

### Step 2: Create `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### Step 3: Deploy
```bash
vercel
```

### Step 4: Add Environment Variables
```bash
vercel env add ASSEMBLYAI_API_KEY
vercel env add OPENAI_API_KEY
# ... etc
```

---

## AWS (Production)

### Using Elastic Beanstalk

1. Install EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize:
   ```bash
   eb init -p python-3.11 voice-agent
   ```

3. Create environment:
   ```bash
   eb create voice-agent-env
   ```

4. Set environment variables:
   ```bash
   eb setenv ASSEMBLYAI_API_KEY=your-key OPENAI_API_KEY=your-key
   ```

5. Deploy:
   ```bash
   eb deploy
   ```

### Using EC2 + Docker

1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

2. Build and run:
   ```bash
   docker build -t voice-agent .
   docker run -p 5000:5000 --env-file .env voice-agent
   ```

---

## Database Setup

### PostgreSQL on Render
1. Create PostgreSQL database in Render
2. Copy connection string
3. Add to environment variables: `DATABASE_URL`

### Supabase (Free PostgreSQL)
1. Go to https://supabase.com
2. Create project
3. Get connection string from Settings → Database
4. Format: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`

### Neon (Serverless PostgreSQL)
1. Go to https://neon.tech
2. Create project
3. Copy connection string
4. Add to `DATABASE_URL`

---

## Post-Deployment Checklist

- [ ] Server is running (check `/health` endpoint)
- [ ] Environment variables are set
- [ ] Database is connected
- [ ] Webhook URL is updated in telephony provider
- [ ] Test incoming call webhook
- [ ] Monitor logs for errors

---

## Troubleshooting

### Server won't start
- Check logs: `railway logs` or Render dashboard
- Verify all environment variables are set
- Check Python version matches `runtime.txt`

### Database errors
- Verify `DATABASE_URL` is correct
- Run migrations: `python -c "from app import app, db; app.app_context().push(); db.create_all()"`

### Webhook not receiving calls
- Verify webhook URL is publicly accessible
- Check telephony provider logs
- Test webhook with: `curl -X POST https://your-url.com/webhook/incoming`

---

## Monitoring

### Health Check
```bash
curl https://your-app.onrender.com/health
```

### View Logs
- Render: Dashboard → Logs
- Railway: `railway logs`
- Vercel: Dashboard → Functions → Logs

---

## Scaling

For production with high call volume:
- Use PostgreSQL (not SQLite)
- Increase gunicorn workers: `-w 8`
- Use Redis for caching
- Set up monitoring (Sentry, DataDog, etc.)
- Use CDN for audio files




