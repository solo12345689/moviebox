# How to Deploy the Backend to Render (Free Cloud Hosting)

You can host the backend on **Render** so it runs 24/7 without your PC or Phone.

## Prerequisites
1.  **GitHub Account**: To host your code.
2.  **Render Account**: Sign up at [render.com](https://render.com).

## Step 1: Push Code to GitHub
1.  Create a new repository on GitHub (e.g., `moviebox-backend`).
2.  Push your `moviebox_web_app` folder to this repository.

## Step 2: Create Service on Render
1.  Go to your Render Dashboard and click **"New + "** -> **"Web Service"**.
2.  Connect your GitHub repository.
3.  Configure the settings:
    *   **Name**: `moviebox-backend` (or similar)
    *   **Region**: Choose one close to you (e.g., Singapore, Frankfurt).
    *   **Branch**: `main` (or master)
    *   **Root Directory**: `backend` (Important: Change this from empty to `backend`)
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
    *   **Instance Type**: `Free`

4.  Click **"Create Web Service"**.

## Step 3: Update the App (CRITICAL)
Once Render finishes building, it will give you a URL (e.g., `https://moviebox-backend.onrender.com`).

You **MUST** update your Android App to talk to this new URL instead of `localhost`.

1.  Open `frontend/src/App.jsx` on your PC.
2.  Find this line (around line 14):
    ```javascript
    const API_BASE = 'http://localhost:8000'; 
    ```
3.  Change it to your Render URL:
    ```javascript
    const API_BASE = 'https://moviebox-backend.onrender.com'; // No trailing slash
    ```
4.  **Rebuild the APK**:
    *   `npm run build`
    *   `npx cap sync`
    *   Open Android Studio and build the APK again.

## Important Warnings
1.  **Free Tier Delay**: Render free servers "sleep" after inactivity. The first request might take 50+ seconds to wake it up.
2.  **Blocking**: Some streaming sites block cloud server IPs (like Render). If search or streaming fails, this is why.
3.  **No MPV on Server**: The "Play on Server" button won't work (obviously). Only "Stream" on your phone will work.
