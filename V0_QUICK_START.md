# 🚀 Quick Start: V0 Dashboard Integration

## Step 1: Copy the Prompt

1. Open **v0.dev**
2. Copy the entire prompt from `V0_PROMPT.md`
3. Paste it into v0.dev
4. Let v0 generate the dashboard

## Step 2: Set Up Environment

After v0 generates the code:

1. Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

2. Install dependencies (if needed):
```bash
npm install
# or
yarn install
```

## Step 3: Start Your Backend

Make sure your Flask server is running:
```bash
cd voice
python app.py
```

## Step 4: Start the Dashboard

```bash
npm run dev
# or
yarn dev
```

Visit: `http://localhost:3000`

## Step 5: Test Integration

1. Make a test call using your backend
2. Check the dashboard - you should see the call appear
3. Click on a call to view transcripts
4. Verify all features work

## Troubleshooting

### CORS Errors
- Check Flask CORS is enabled
- Verify API URL in `.env.local`

### No Data Showing
- Check Flask server is running
- Verify API endpoints return data
- Check browser console for errors

### API Connection Failed
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check Flask server is accessible
- Test API directly: `curl http://localhost:5000/health`

---

**Your dashboard will be ready to use!** 🎉
