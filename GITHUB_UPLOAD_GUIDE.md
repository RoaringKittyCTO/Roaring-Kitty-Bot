# Upload Your Roaring Kitty Bot to GitHub

## Step 1: Create GitHub Account (if needed)

1. Go to https://github.com
2. Click "Sign up" if you don't have an account
3. Choose a username and verify your email

## Step 2: Create New Repository

1. Click the "+" icon in top right corner
2. Select "New repository"
3. Repository name: `roaring-kitty-bot` (or your choice)
4. Description: "Telegram bot for monitoring Roaring Kitty token with custom notifications"
5. Set to "Public" (required for free Render deployment)
6. Check "Add a README file"
7. Click "Create repository"

## Step 3: Download Files from Replit

From your current Replit project, download these files:

### Core Bot Files:
- `main.py`
- `bot_handler_new.py`
- `dexscreener_monitor.py`
- `image_generator.py`
- `code_executor.py`
- `security_config.py`

### Configuration Files:
- `render.yaml`
- `Dockerfile`
- `railway.json`

### Documentation:
- `README.md`
- `RENDER_DEPLOYMENT.md`
- `DEPLOYMENT.md`

### Background Image:
- `attached_assets/Party Energy with a Cartoon Twist_1751143536514.png`

**How to download from Replit:**
1. Click on each file in the file explorer
2. Right-click and select "Download"
3. Save to a folder on your computer

## Step 4: Upload to GitHub

### Method A: GitHub Web Interface (Easiest)

1. Go to your new repository on GitHub
2. Click "uploading an existing file"
3. Drag and drop all downloaded files
4. Create folder structure:
   - Create `attached_assets` folder
   - Upload your party image inside it
5. Scroll down to "Commit changes"
6. Title: "Initial bot upload with Roaring Kitty monitoring"
7. Click "Commit changes"

### Method B: Git Commands (Advanced)

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/roaring-kitty-bot.git
cd roaring-kitty-bot

# Copy all your bot files into this folder
# Including the attached_assets folder with your party image

# Add files to git
git add .

# Commit files
git commit -m "Initial bot upload with Roaring Kitty monitoring"

# Push to GitHub
git push origin main
```

## Step 5: Verify Upload

Check your GitHub repository contains:
```
├── main.py
├── bot_handler_new.py
├── dexscreener_monitor.py
├── image_generator.py
├── code_executor.py
├── security_config.py
├── attached_assets/
│   └── Party Energy with a Cartoon Twist_1751143536514.png
├── render.yaml
├── Dockerfile
├── README.md
└── RENDER_DEPLOYMENT.md
```

## Step 6: Repository Settings

1. Go to repository "Settings" tab
2. Scroll to "Pages" section
3. Ensure "Source" is set to "Deploy from a branch"
4. This enables GitHub Pages (optional)

## Important Security Notes

- **NEVER upload your bot token to GitHub**
- The code is configured to use environment variables
- Your actual token will be added in Render settings

## Next Steps

Once uploaded to GitHub:
1. Go to render.com
2. Connect your GitHub account
3. Select your `roaring-kitty-bot` repository
4. Add `TELEGRAM_BOT_TOKEN` environment variable
5. Deploy automatically

## Troubleshooting

**File too large error:**
- GitHub has 25MB file limit
- Your party image should be under this limit

**Permission denied:**
- Make sure repository is public
- Check you're logged into correct GitHub account

**Missing files:**
- Verify all files downloaded from Replit
- Check folder structure matches exactly

Your bot will then be ready for 24/7 deployment on Render, monitoring the real Roaring Kitty token contract and sending custom notifications with your party background image.