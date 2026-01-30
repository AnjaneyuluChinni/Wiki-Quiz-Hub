# Render Deployment Guide

## Full Deployment Instructions for Wiki Quiz Hub

This guide covers deploying the FastAPI backend and React frontend to Render.

## Part 1: Deploy Backend to Render

### Prerequisites
- GitHub account with the code pushed
- Render account (sign up at render.com)
- OpenAI or Google Gemini API key (optional for production)

### Step 1: Create PostgreSQL Database on Render

1. Go to [render.com](https://render.com) dashboard
2. Click **New +** → **PostgreSQL**
3. Fill in details:
   - **Name:** `wiki-quiz-db`
   - **Database:** `wiki_quiz`
   - **User:** `wiki_user`
   - **Region:** Choose same as API (e.g., `Frankfurt`)
   - **PostgreSQL Version:** `14`
   - **Instance Type:** `Free` (upgrade if needed)
4. Click **Create Database**
5. **Copy the connection string** (you'll need it for the API service)

### Step 2: Deploy API Backend

1. Go to [render.com](https://render.com) dashboard
2. Click **New +** → **Web Service**
3. Select your GitHub repository with the code
4. Fill in configuration:

   ```
   Name: wiki-quiz-api
   Environment: Python 3
   Region: Frankfurt (same as DB)
   Branch: main
   
   Build Command:
   pip install -r backend/requirements.txt
   
   Start Command:
   cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   
   Instance Type: Free
   ```

5. Click **Create Web Service**
6. Wait for deployment to complete (2-3 minutes)

### Step 3: Add Environment Variables to API Service

After deployment, go to the service settings:

1. **Environment** tab
2. Add the following variables:

   ```
   DATABASE_URL=postgres://user:password@host:port/wiki_quiz
   OPENAI_API_KEY=sk_your_key_here
   DEBUG=False
   ALLOWED_ORIGINS=https://wiki-quiz-hub.onrender.com,http://localhost:3000
   ```

   Replace:
   - `DATABASE_URL` with the PostgreSQL connection string from Step 1
   - `OPENAI_API_KEY` with your actual API key (or leave blank to use dummy data)

3. Click **Save**
4. The service will redeploy automatically

### Step 4: Initialize Database

1. Go to service dashboard
2. Click the **Shell** tab
3. Run:
   ```bash
   cd backend
   python seed_database.py
   ```
4. This creates tables and seeds sample data

### Step 5: Test the API

Visit: `https://wiki-quiz-api.onrender.com/docs`

You should see the Swagger API documentation.

Test with:
```bash
curl -X POST https://wiki-quiz-api.onrender.com/api/quizzes/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://en.wikipedia.org/wiki/Albert_Einstein"}'
```

---

## Part 2: Deploy Frontend to Render

### Step 1: Configure Frontend API Endpoint

Update your React app to use the deployed backend:

**File:** `client/src/lib/queryClient.ts`

```typescript
const API_BASE = import.meta.env.VITE_API_URL || 
  (import.meta.env.MODE === 'production'
    ? 'https://wiki-quiz-api.onrender.com'
    : 'http://localhost:8000');
```

Or in **client/src/main.tsx** or API config:

```typescript
const apiUrl = 'https://wiki-quiz-api.onrender.com';
```

### Step 2: Create Render Deployment File

Create `render.yaml` in project root:

```yaml
services:
  - type: web
    name: wiki-quiz-frontend
    env: node
    region: frankfurt
    plan: free
    branch: main
    buildCommand: cd client && npm install && npm run build
    startCommand: cd client && npm run preview
    envVars:
      - key: VITE_API_URL
        value: https://wiki-quiz-api.onrender.com

  - type: web
    name: wiki-quiz-api
    env: python
    region: frankfurt
    plan: free
    branch: main
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        value: ${DB_URL}
      - key: DEBUG
        value: 'False'

  - type: pserv
    name: wiki-quiz-db
    region: frankfurt
    plan: free
    ipAllowList: []
```

### Step 3: Deploy Frontend

1. Go to Render dashboard
2. Click **New +** → **Web Service**
3. Select your repository
4. Configuration:
   ```
   Name: wiki-quiz-frontend
   Environment: Node
   Region: Frankfurt
   
   Build Command:
   cd client && npm install && npm run build
   
   Start Command:
   cd client && npm run preview
   
   Instance Type: Free
   ```

5. Add Environment Variables:
   ```
   VITE_API_URL=https://wiki-quiz-api.onrender.com
   ```

6. Click **Create Web Service**

### Step 4: Test Frontend

Visit: `https://wiki-quiz-frontend.onrender.com`

---

## Part 3: Monitoring and Troubleshooting

### View Logs

**Backend Logs:**
1. Go to wiki-quiz-api service
2. Click **Logs** tab
3. Check for errors

**Frontend Logs:**
1. Go to wiki-quiz-frontend service
2. Click **Logs** tab

### Common Issues and Solutions

#### Issue: "Database connection failed"
**Solution:**
1. Verify DATABASE_URL in environment variables
2. Check PostgreSQL instance is running
3. Ensure IP is whitelisted (if applicable)

```bash
# Test connection from shell:
psql $DATABASE_URL
```

#### Issue: "CORS error in frontend"
**Solution:**
Update `ALLOWED_ORIGINS` in backend environment:
```
ALLOWED_ORIGINS=https://wiki-quiz-frontend.onrender.com,https://wiki-quiz-api.onrender.com,http://localhost:3000
```

#### Issue: "Module not found error"
**Solution:**
1. Check all dependencies in `requirements.txt`
2. Check `package.json` in client folder
3. Rebuild the service (click **Manual Deploy**)

#### Issue: "502 Bad Gateway"
**Solution:**
1. Service might be starting up (free tier can be slow)
2. Check logs for errors
3. Increase timeout or upgrade to paid instance

### Monitor Performance

1. Go to service dashboard
2. Click **Metrics** tab
3. Monitor:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### Scaling Up

**To handle more traffic:**
1. Upgrade to **Starter** or **Standard** instance
2. Database: Upgrade from **Free** PostgreSQL
3. Add custom domain for branding

---

## Part 4: Continuous Deployment

### Auto-Deploy on Push

By default, Render auto-deploys when you push to the main branch.

To change:
1. Service settings → **Deploy** tab
2. Modify branch or webhook settings

### Manual Deploy

1. Service dashboard
2. Click **Manual Deploy** button
3. Choose branch
4. Click **Deploy**

### Environment Variables Management

Keep sensitive data in `.env` files locally:

**Don't commit:**
```bash
echo ".env" >> .gitignore
```

**Always set in Render dashboard:**
- API keys
- Database credentials
- Secret tokens

---

## Part 5: Custom Domain Setup (Optional)

### Add Custom Domain

1. Service settings → **Domains**
2. Click **Add Custom Domain**
3. Enter: `api.yoursite.com`
4. Add DNS record to your domain provider:
   ```
   Type: CNAME
   Name: api
   Value: wiki-quiz-api.onrender.com
   ```

---

## Deployment Checklist

- [ ] PostgreSQL created and running
- [ ] Backend deployed to Render
- [ ] Environment variables configured
- [ ] Database initialized with sample data
- [ ] Backend API accessible at `/docs`
- [ ] Frontend configured with correct API URL
- [ ] Frontend deployed to Render
- [ ] Frontend loads and connects to backend
- [ ] Quiz generation works end-to-end
- [ ] History/past quizzes load correctly
- [ ] Error handling works (test invalid URL)
- [ ] Custom domain added (optional)
- [ ] Monitoring dashboards reviewed
- [ ] Team has access to logs and metrics

---

## Support Resources

- **Render Docs:** https://render.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

## Cost Estimation (as of Jan 2024)

| Resource | Free Tier | Cost |
|----------|-----------|------|
| Web Service (API) | 750 hrs/month | $7/month |
| Web Service (Frontend) | 750 hrs/month | $7/month |
| PostgreSQL | 256 MB | $15/month |
| **Total** | **Free tier** | **~$29/month** |

---

## Success! 🎉

Your Wiki Quiz Hub is now live! Share the URL with others to generate and take quizzes from Wikipedia articles.
