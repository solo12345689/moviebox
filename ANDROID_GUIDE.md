# How to Build the Android App (APK)



## Prerequisites

1.  **Install Android Studio**: Download and install it from [developer.android.com/studio](https://developer.android.com/studio).
2.  **Install Android SDK**: During installation, make sure to install the "Android SDK" and "Android SDK Command-line Tools".

## Steps to Build

1.  **Open a Terminal** (Command Prompt or PowerShell) and navigate to the `frontend` folder:
    ```bash
    cd C:\Users\akshi\.gemini\antigravity\scratch\moviebox_web_app\frontend
    ```

2.  **Add Android Platform** (if you haven't already):
    ```bash
    npx cap add android
    ```
    *Note: If this command fails, make sure Android Studio is installed and the `ANDROID_HOME` environment variable is set.*

3.  **Sync Project**:
    ```bash
    npx cap sync
    ```

4.  **Open in Android Studio**:
    ```bash
    npx cap open android
    ```
    This will launch Android Studio with your project.

5.  **Build the APK**:
    *   In Android Studio, wait for Gradle sync to finish.
    *   Go to **Build** > **Build Bundle(s) / APK(s)** > **Build APK(s)**.
    *   Once finished, a notification will appear. Click **locate** to find your `.apk` file.

6.  **Install on Phone**:
    *   Transfer the `.apk` file to your Android phone.
    *   Open it to install (you may need to enable "Install from unknown sources").

## Troubleshooting

*   **"SDK location not found"**: Create a file named `local.properties` in the `android` folder and add: `sdk.dir=C:\\Users\\<YOUR_USER>\\AppData\\Local\\Android\\Sdk` (replace `<YOUR_USER>` with your actual username).
*   **Gradle Errors**: Try clicking "Sync Project with Gradle Files" (elephant icon) in Android Studio.
