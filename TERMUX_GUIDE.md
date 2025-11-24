# How to Run the Backend on Android (No PC Required)

If you want to use the app completely offline or without a PC, you can run the backend directly on your phone using **Termux**.

## Prerequisites

1.  **Install Termux**: Download it from F-Droid (recommended) or the Play Store.
2.  **Install the APK**: Install the `app-debug.apk` you built earlier.

## Step 1: Setup Termux

Open Termux and run these commands one by one (press Enter after each):

1.  **Update packages:**
    ```bash
    pkg update && pkg upgrade
    ```

2.  **Install Python and Git:**
    ```bash
    pkg install python git clang make libjpeg-turbo
    ```

3.  **Grant Storage Permission:**
    ```bash
    termux-setup-storage
    ```
    (Click "Allow" in the popup)

## Step 2: Get the Code

You need to copy the `backend` folder to your phone.
*   **Option A (Easy):** Zip the `backend` folder on your PC, send it to your phone, and extract it.
*   **Option B (Git):** If you pushed this code to GitHub, just clone it:
    ```bash
    git clone https://github.com/your-username/moviebox-web-app.git
    cd moviebox-web-app
    ```

## Step 3: Install Dependencies

Navigate to the folder where you put the code (e.g., `Downloads/backend` or `moviebox-web-app/backend`).

```bash
cd storage/downloads/backend  # Example path
pip install fastapi uvicorn moviebox-api
```

*Note: If `moviebox-api` fails to install due to compilation errors, you might need additional packages like `libxml2`, `libxslt`, or `rust`.*

## Step 4: Run the Backend

Start the server:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Step 5: Configure the App

1.  Open the **MovieBox App** on your phone.
2.  Since the backend is running locally on the phone, the app should connect to `http://localhost:8000` (which is the default).
3.  You can now search and stream directly on your phone!

## Important Notes

*   **Background Usage**: Termux must stay open in the background. You can acquire a "Wake Lock" in the Termux notification to prevent Android from killing it.
*   **Battery**: Running a server will consume more battery.
