# Image Optimizer

**Image Optimizer** is a web application that helps you **shrink image file sizes** while keeping them usable. You upload an image, choose a compression quality, and get back a smaller version that’s easier to store or share.

## What it does

- **Upload** an image (PNG, JPG, or GIF).
- **Resize** it to 50% of its original width and height.
- **Compress** it as a JPEG so the file size goes down.
- **Compare** the original and the optimized image side by side and see how much smaller the file became.
- **Download** the optimized image.

The goal is to **reduce file size** (often by a large percentage) so images load faster and take less space, without losing too much visual quality. You control the trade-off with a **quality slider** (0–100): lower quality means smaller files; higher quality keeps more detail.

## Who it’s for

- Anyone who wants to **make images smaller** for websites, email, or storage.
- Developers who want a **simple, runnable example** of image optimization (resize + JPEG compression) with a web UI and API.

## What’s in this repo

- **Backend** (`ImageOptimizer.app/`) – A small Flask (Python) server that receives your image, resizes and compresses it with OpenCV, and sends back the result.
- **Frontend** (`ImageOptimizer.web/my-react-app/`) – A React app where you pick a file, set quality, upload, and see before/after with file sizes and a download link.

For detailed setup, API, and code layout, see **[PROGRAMMER.md](PROGRAMMER.md)**.

## Prerequisites

- **Python:** 3.13 (recommended) — the project uses Python 3.13 as listed in `.python-version`. A Python 3.11+ interpreter should also work but 3.13 is recommended.
- **pip:** Python package installer (bundled with recent Python).
- **Virtualenv:** Recommended to isolate dependencies (`python -m venv .venv`).
- **Node.js + npm:** Required to run the frontend (`Node 16+`, `npm` or `yarn`; Node 18 LTS recommended).
- **Git:** Useful for cloning the repo (optional if you already have the files).
- **Platform-specific (optional):**
  - On Linux, you may need system packages for OpenCV (e.g. `libgl1`, `libglib2.0-0`) if wheel installation fails.
  - On Windows/macOS the `opencv-python` wheel usually installs without additional system dependencies.

These prerequisites cover the development/run environment for both the Flask backend and the React frontend.

## Quick start


1. **Install and run the backend**
   Setup environment variables

   - **Backend**: `SECRET_KEY` — optional. The backend reads `SECRET_KEY` from the environment (`os.environ.get('SECRET_KEY')`) and falls back to a generated token if not set. To run the Flask dev server with a specific key, set the environment variable before starting the app.

   - **Frontend**: `VITE_API_URL` — the React app reads the backend base URL from `import.meta.env.VITE_API_URL`. Create `ImageOptimizer.web/my-react-app/.env.local` (or use `.env`) and add `VITE_API_URL=http://localhost:5000`. Environment variables used by Vite must be prefixed with `VITE_`.

   - **Optional**: If you prefer `flask run`, set `FLASK_APP=run.py` (and optionally `FLASK_ENV=development`) in your shell.

   Examples:

   - PowerShell:
     ```powershell
     $env:SECRET_KEY = 'your-secret'
     # Create frontend .env.local (one-time):
     # echo 'VITE_API_URL=http://localhost:5000' > ImageOptimizer.web/my-react-app/.env.local
     ```

   - Bash (macOS / Linux):
     ```bash
     export SECRET_KEY='your-secret'
     # Create frontend .env.local (one-time):
     echo 'VITE_API_URL=http://localhost:5000' > ImageOptimizer.web/my-react-app/.env.local
     ```

   - Note: `UPLOAD_FOLDER` is configured in `ImageOptimizer.app/app/config.py` and is not read from environment variables by default.

   Install and run the Flask backend (detailed).

   - Create and activate a virtual environment (recommended):

     - Windows (PowerShell):
       ```powershell
       python -m venv .venv
       .\.venv\Scripts\Activate.ps1
       ```

     - Windows (cmd):
       ```cmd
       python -m venv .venv
       .\.venv\Scripts\activate.bat
       ```

     - macOS / Linux:
       ```bash
       python3 -m venv .venv
       source .venv/bin/activate
       ```

   - Install the backend dependencies:

     - From the project root:
       ```bash
       pip install -r ImageOptimizer.app/requirements.txt
       ```

     - Or from inside the backend folder:
       ```bash
       cd ImageOptimizer.app
       pip install -r requirements.txt
       ```

   - Run the backend server:

     - From the project root:
       ```bash
       python ImageOptimizer.app/run.py
       ```

     - Or from inside the backend folder:
       ```bash
       cd ImageOptimizer.app
       python run.py
       ```

   - Notes:
     - The development server starts on `http://127.0.0.1:5000` by default and `run.py` enables Flask debug mode.
     - To stop the server press `Ctrl+C` in the terminal.

2. **Run the frontend** (in a new terminal):
   ```bash
   cd ImageOptimizer.web/my-react-app
   npm install
   npm run dev
   ```
   Open the URL shown (e.g. `http://localhost:5173`), upload an image, adjust quality, and click **Upload & Optimize**.



**Repository:** [https://github.com/Bhaveshb1986/Image_Optimizer.git]


## Summary

**Objective:** Make it easy to **optimize images** by resizing and compressing them so file sizes drop and images stay good enough for typical use. The code demonstrates this with a web UI and a simple backend API that anyone can run and extend.
