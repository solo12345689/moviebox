# MovieBox Web App

A modern, cinematic web interface for searching, streaming, and downloading movies, TV series, and anime. Built with FastAPI and React.

## Features

- **Cinematic UI**: A premium "Cinematic Dark" theme with glassmorphism effects and smooth animations.
- **Unified Search**: Search across movies, TV series, and anime with a single powerful search bar.
- **Streaming**: Instantly stream content using `mpv` player integration.
- **Downloading**: Download content directly to your local machine with progress tracking.
- **Responsive Design**: Optimized for both desktop (laptops) and mobile devices.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.8+**: For the backend server.
2.  **Node.js 16+**: For the frontend development server.
3.  **mpv Media Player**: Required for streaming functionality.
    *   **Windows**: Download from [mpv.io](https://mpv.io/installation/) and ensure `mpv.exe` is in your system PATH.
    *   **Linux/Mac**: Install via your package manager (e.g., `apt install mpv` or `brew install mpv`).

## Installation

### 1. Backend Setup

Navigate to the project root directory:

```bash
cd moviebox_web_app
```

Install the required Python dependencies:

```bash
pip install fastapi uvicorn requests moviebox-api
```
*(Note: Ensure `moviebox-api` is properly installed or available in your python path)*

### 2. Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install the Node.js dependencies:

```bash
npm install
```

## Running the Application

You need to run both the backend and frontend servers.

### 1. Start the Backend

From the project root (`moviebox_web_app`), run:

```bash
start_backend.bat
```

*Or manually:*
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`.

### 2. Start the Frontend

From the `frontend` directory, run:

```bash
npm run dev
```

The web application will be available at `http://localhost:5173`.

## Usage

1.  Open `http://localhost:5173` in your browser.
2.  **Search**: Enter a title (e.g., "Naruto", "Inception") in the search bar.
3.  **View Details**: Click on a movie or show card to view details.
4.  **Stream**: Click the "Stream" button to open the video in `mpv` player.
5.  **Download**: Click "Download" to save the file. Progress will be shown in the modal.

## Troubleshooting

-   **Search is slow on first run**: The backend performs a "warmup" routine on startup. Give it a few seconds after starting the server before searching.
-   **Stream fails**: Ensure `mpv` is installed and added to your system's PATH. You can verify this by running `mpv --version` in your terminal.
-   **No results**: Try a different search term. The application relies on the `moviebox-api` for content.

## Project Structure

-   `backend/`: FastAPI backend code.
    -   `api.py`: Core API logic and endpoints.
    -   `main.py`: App entry point and CORS config.
-   `frontend/`: React frontend code.
    -   `src/components/`: Reusable UI components (MovieCard, SearchBar, DetailsModal).
    -   `src/styles/`: Global CSS and design system.
