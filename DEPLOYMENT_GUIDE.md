# Promptsmith Deployment Guide

This guide will help you deploy the Promptsmith Chart Optimizer API and connect it to your website.

## 🚀 Quick Start Options

### Option 1: Railway (Recommended - Free Tier Available)
1. **Deploy to Railway:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Deploy from Promptsmith directory
   cd /path/to/Promptsmith
   railway init
   railway up
   ```

2. **Set Environment Variables in Railway Dashboard:**
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `PORT`: 8000 (auto-set by Railway)

3. **Get your API URL:**
   - Railway will provide a URL like: `https://your-app-name.railway.app`

### Option 2: Render (Free Tier Available)
1. **Connect your GitHub repo to Render**
2. **Create a new Web Service**
3. **Set build command:** `pip install -r requirements.txt`
4. **Set start command:** `uvicorn api_server:app --host=0.0.0.0 --port=$PORT`
5. **Set environment variables:**
   - `OPENAI_API_KEY`: Your OpenAI API key

### Option 3: Heroku
1. **Install Heroku CLI and login**
2. **Deploy:**
   ```bash
   cd /path/to/Promptsmith
   heroku create your-promptsmith-app
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```
3. **Set environment variables:**
   ```bash
   heroku config:set OPENAI_API_KEY=your-api-key
   ```

## 🔧 Local Testing

Before deploying, test the API locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY=your-api-key

# Run the API server
python api_server.py

# Test the API
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Create a bar chart showing sales data", "max_iterations": 3}'
```

## 🌐 Connect to Your Website

### Step 1: Deploy Promptsmith API
Follow one of the deployment options above to get your API URL.

### Step 2: Update Website Environment Variables
In your Vercel dashboard for your website:

1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add:
   - `PROMPTSMITH_API_URL`: Your deployed API URL (e.g., `https://your-app.railway.app`)

### Step 3: Deploy Website Updates
The website code is already updated to call the real API. Just deploy:

```bash
cd /path/to/your/website
vercel --prod
```

## 🔍 Testing the Integration

1. **Test the API directly:**
   ```bash
   curl -X POST https://your-api-url/optimize \
     -H "Content-Type: application/json" \
     -d '{"user_query": "Show me a line chart of revenue over time"}'
   ```

2. **Test from your website:**
   - Open your website
   - Open the AI chat
   - Ask for a chart: "Create a bar chart showing sales data"

## 🛠️ Troubleshooting

### API Not Responding
- Check if your API is deployed and running
- Verify environment variables are set correctly
- Check API logs for errors

### CORS Issues
- The API includes CORS headers, but you may need to update `allow_origins` in `api_server.py`
- For production, replace `"*"` with your actual domain

### OpenAI API Errors
- Verify your `OPENAI_API_KEY` is valid and has credits
- Check OpenAI API status page

### Fallback Mode
If the real API fails, the website will automatically fall back to mock responses. You'll see `"fallback": true` in the response.

## 📊 Monitoring

### API Health Check
```bash
curl https://your-api-url/
```

### Cache Statistics
```bash
curl https://your-api-url/cache/stats
```

### Clear Cache
```bash
curl -X DELETE https://your-api-url/cache
```

## 🔄 Updates and Maintenance

### Updating the API
1. Make changes to your Promptsmith code
2. Commit and push to your repository
3. Redeploy using your platform's method

### Updating the Website
1. Make changes to your website code
2. Deploy with `vercel --prod`

## 💰 Cost Considerations

- **Railway**: Free tier includes 500 hours/month
- **Render**: Free tier available
- **Heroku**: Free tier discontinued, paid plans start at $7/month
- **OpenAI API**: Pay per use, typically $0.01-0.10 per chart generation

## 🎯 Production Checklist

- [ ] API deployed and accessible
- [ ] Environment variables configured
- [ ] Website updated with API URL
- [ ] CORS configured for your domain
- [ ] Error handling and fallbacks working
- [ ] Monitoring and logging set up
- [ ] Cost monitoring enabled

## 📞 Support

If you encounter issues:
1. Check the API logs in your deployment platform
2. Verify all environment variables are set
3. Test the API endpoint directly
4. Check the browser console for errors

The system includes comprehensive error handling and will fall back to mock responses if the real API is unavailable. 