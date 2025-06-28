# Deploy Your Roaring Kitty Bot to Render (Free 24/7 Hosting)

## Step 1: Prepare Your Files

First, you'll need to upload your bot to GitHub. Create a new repository with these files:

### Required Files:
- `main.py` (your bot entry point)
- `bot_handler_new.py` (main bot logic)
- `dexscreener_monitor.py` (token monitoring)
- `image_generator.py` (custom image creation)
- `code_executor.py` (Python REPL)
- `security_config.py` (security settings)
- `render.yaml` (already created - Render configuration)
- `Dockerfile` (already created - container setup)
- `attached_assets/Party Energy with a Cartoon Twist_1751143536514.png` (your party background)

## Step 2: Deploy to Render

1. **Go to Render.com**
   - Visit https://render.com
   - Click "Get Started for Free"
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"
   - Choose "Build and deploy from a Git repository"

3. **Connect Repository**
   - Connect your GitHub account
   - Select your bot repository
   - Click "Connect"

4. **Configure Service**
   - Render will auto-detect your `render.yaml` file
   - Service Name: `roaring-kitty-bot` (or your choice)
   - Environment: `Python`
   - Build Command: `pip install python-telegram-bot RestrictedPython Pillow requests web3`
   - Start Command: `python main.py`

5. **Add Environment Variable**
   - In the service settings, go to "Environment"
   - Click "Add Environment Variable"
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: Your actual bot token (starts with numbers like 8005502972:AAE...)
   - Click "Save Changes"

6. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your bot
   - This takes 2-3 minutes

## Step 3: Verify Deployment

Once deployed, your bot will:
- Start automatically and stay running 24/7
- Monitor the real Roaring Kitty token contract
- Send notifications with your custom party images
- Handle Python code execution requests

## Render Free Tier Benefits

- **750 hours/month** (more than enough for 24/7)
- **Automatic deployments** from GitHub
- **Health checks** and auto-restart
- **HTTPS** enabled by default
- **Log monitoring** available

## Important Notes

1. **Bot Token Security**: Never commit your actual bot token to GitHub. Always use environment variables.

2. **Auto-Sleep**: Free tier sleeps after 15 minutes of inactivity, but Telegram bots stay active with constant polling.

3. **Logs**: Check your deployment logs in Render dashboard if needed.

4. **Updates**: Push changes to GitHub, and Render will auto-deploy.

## Expected Bot Behavior

Your bot will:
- Respond to `/start_roar` by monitoring real Roaring Kitty token
- Generate custom images with remaining token counts
- Send notifications when new buys are detected
- Process Python code execution safely
- Run continuously without interruption

## Troubleshooting

If deployment fails:
1. Check build logs in Render dashboard
2. Verify all files are in your GitHub repository
3. Ensure bot token is set correctly in environment variables
4. Check that `render.yaml` configuration is correct

Your Roaring Kitty monitoring bot will be live and monitoring the real token contract `0xD8C978de79E12728e38aa952a6cB4166F891790f` 24/7!