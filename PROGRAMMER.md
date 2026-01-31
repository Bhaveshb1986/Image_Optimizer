# Image Optimizer – Programmer Summary

This document summarizes the **AI Image Optimizer** application for developers who want to work on the codebase. It covers architecture, setup, API, and where to make changes.

---

## 1. Overview

The application lets users **upload an image**, optionally set **JPEG quality**, and receive a **resized (50%) and compressed** version. It consists of:

- **Backend (Flask)** – `ImageOptimizer.app/` – handles uploads, image processing (OpenCV), and file serving.
- **Frontend (React + Vite)** – `ImageOptimizer.web/my-react-app/` – upload UI, quality slider, before/after comparison, and download.

There is also a **server-rendered HTML** variant in the backend templates (`index.html` with inline JS) that uses the same `/upload` API.

---

## 2. Repository Layout

```
AI_Image_Optimizer_self/
├── main.py                    # Root entry (placeholder "Hello" script)
├── pyproject.toml             # Root Python project (uv); Python ≥3.13
├── PROGRAMMER.md              # This file
├── samples/                   # Sample images for testing
│
├── ImageOptimizer.app/        # Backend (Flask)
│   ├── run.py                 # App entry: creates app, runs dev server
│   ├── requirements.txt       # Flask, flask-cors, opencv-python, Pillow
│   ├── TODO.md
│   └── app/
│       ├── __init__.py        # create_app(); registers blueprint, CORS, Config
│       ├── config.py          # SECRET_KEY, UPLOAD_FOLDER (app/uploads)
│       ├── models.py          # Empty (no DB yet)
│       ├── routes.py          # Blueprint: /, POST /upload, /uploads/<filename>, /favicon.ico
│       ├── static/            # style.css
│       ├── templates/         # base.html, index.html (HTML form + fetch)
│       └── uploads/           # Processed images (processed_*.jpg); created at runtime
│
└── ImageOptimizer.web/        # Frontend
    └── my-react-app/
        ├── package.json       # React 19, Vite 7
        ├── vite.config.js     # Vite + React plugin
        ├── .env.example       # VITE_API_URL=http://localhost:5000
        ├── index.html
        └── src/
            ├── main.jsx       # React root
            ├── App.jsx        # Main UI: upload form, quality, results grid
            ├── App.css
            └── index.css
```

---

## 3. Backend (ImageOptimizer.app)

### 3.1 Stack

- **Flask** – Web app and routing.
- **flask-cors** – CORS enabled for all origins so the React app can call the API.
- **OpenCV (cv2)** – Resize to 50% and JPEG encode with configurable quality.
- **Pillow (PIL)** – Content-based image validation (after saving temp file).

### 3.2 Entry Point

- Run the dev server: from `ImageOptimizer.app/` run `python run.py` (or `flask run` with `FLASK_APP=run.py`). Default: `http://localhost:5000`.

### 3.3 Configuration (`app/config.py`)

- **SECRET_KEY** – From env or `secrets.token_hex(16)`.
- **UPLOAD_FOLDER** – `app/uploads/` (relative to `app` package). Processed files are stored here.

### 3.4 Routes (`app/routes.py`)

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Renders `index.html` (server-rendered form). |
| `/upload` | POST | Accepts `image` (file) and optional `quality` (0–100). Resizes to 50%, saves as JPEG, returns JSON. |
| `/uploads/<filename>` | GET | Serves files from `UPLOAD_FOLDER` (e.g. `processed_foo.jpg`). |
| `/favicon.ico` | GET | Returns 204 No Content. |

### 3.5 Upload Flow (POST /upload)

1. Read `image` from `request.files`; validate extension (png, jpg, jpeg, gif) and MIME.
2. Save to temp file in `UPLOAD_FOLDER`; verify with `PIL.Image.open(...).verify()`.
3. Parse `quality` from form (default 50); clamp to 0–100.
4. Load with `cv2.imread`, resize to 50% width/height, encode as JPEG with `cv2.IMWRITE_JPEG_QUALITY`.
5. Save as `processed_<basename>.jpg` in `UPLOAD_FOLDER`.
6. Compute original vs processed size and size-reduction percentage.
7. Remove temp file; return JSON (see below).

**Response (success):**

```json
{
  "message": "Image uploaded and processed successfully!",
  "processed_image": "processed_myfile.jpg",
  "original_size": 123456,
  "processed_size": 45678,
  "size_reduction_percent": 62.95
}
```

**Error responses:** `400` (no file, invalid type, invalid image), `500` (server/disk/OpenCV errors). Body: `{ "error": "..." }`.

### 3.6 Dependencies (Backend)

- **requirements.txt** (in `ImageOptimizer.app/`): Flask, flask-cors, opencv-python, Pillow.
- **pyproject.toml** (root): Can be used with `uv`; lists flask, opencv-python, pillow, python-dotenv; Python ≥3.13.

---

## 4. Frontend (ImageOptimizer.web / my-react-app)

### 4.1 Stack

- **React 19** – UI.
- **Vite 7** – Build and dev server.
- No state library (useState only).
- No router – single page.

### 4.2 Entry Point and Config

- **Entry:** `src/main.jsx` mounts `App` in `#root`.
- **API base URL:** `import.meta.env.VITE_API_URL` (default `http://localhost:5000`). Copy `.env.example` to `.env.local` and set `VITE_API_URL` if the backend runs elsewhere.

### 4.3 Main Component (`src/App.jsx`)

- **State:** `selectedFile`, `preview` (data URL), `quality` (0–100), `loading`, `message`, `error`, `processedImage` (URL), `originalSize`, `processedSize`, `sizeReduction`.
- **Handlers:**
  - **handleFileChange** – Validates type (PNG, JPEG, GIF), sets file + preview, clears result state.
  - **handleSubmit** – Builds `FormData` with `image` and `quality`, POSTs to `${API_URL}/upload`, then sets message, processed image URL, and size stats (or error).
  - **handleReset** – Clears file, preview, result, and resets quality to 50.
- **UI:** File input, quality slider, Submit / Reset; error/success messages; two-column grid: Original (preview + size) and Processed (image + size + reduction % + download link).
- **Helper:** `formatFileSize(bytes)` for human-readable sizes.

### 4.4 API Usage (Frontend)

- **POST** `${VITE_API_URL}/upload`  
  - Body: `FormData` with keys `image` (File), `quality` (string number).  
  - Success: JSON with `processed_image`, `original_size`, `processed_size`, `size_reduction_percent`.  
  - Processed image URL: `${VITE_API_URL}/uploads/${data.processed_image}`.

### 4.5 Scripts (package.json)

- `npm run dev` – Vite dev server (default port, e.g. 5173).
- `npm run build` – Production build.
- `npm run preview` – Preview production build.
- `npm run lint` – ESLint.

---

## 5. Running the Application

1. **Backend**
   - From project root or `ImageOptimizer.app/`:
     - With venv + requirements: `pip install -r ImageOptimizer.app/requirements.txt` then `python ImageOptimizer.app/run.py`.
     - Or with uv: `uv run python ImageOptimizer.app/run.py` (if deps are in pyproject.toml).
   - Backend runs at `http://localhost:5000`.

2. **Frontend**
   - `cd ImageOptimizer.web/my-react-app`
   - `npm install`
   - Create `.env.local` from `.env.example` and set `VITE_API_URL=http://localhost:5000` if needed.
   - `npm run dev`
   - Open the Vite URL (e.g. `http://localhost:5173`).

3. **Quick test**
   - Use sample images in `samples/` or any PNG/JPG/GIF.
   - In React app: choose file, set quality, click “Upload & Optimize”; compare original vs processed and download.

---

## 6. Where to Change What

| Goal | Location |
|------|----------|
| Add/change API routes | `ImageOptimizer.app/app/routes.py` |
| Change upload folder or app config | `ImageOptimizer.app/app/config.py` |
| Change resize ratio or format (e.g. PNG, WebP) | `ImageOptimizer.app/app/routes.py` (OpenCV resize + encode) |
| Adjust allowed file types (backend) | `ImageOptimizer.app/app/routes.py` – `allowed_extensions`, `allowed_mime_types`, Pillow verification |
| Backend app factory / CORS / blueprints | `ImageOptimizer.app/app/__init__.py` |
| Upload UI, quality slider, result display | `ImageOptimizer.web/my-react-app/src/App.jsx` |
| Styling | `App.css`, `index.css`; backend: `app/static/style.css`, templates |
| Server-rendered upload page | `ImageOptimizer.app/app/templates/index.html` |
| Frontend API base URL | `.env.local` with `VITE_API_URL` |

---

## 7. Conventions and Notes

- **Processing:** All outputs are JPEG; resize is fixed at 50%. Quality is the only variable (0–100).
- **Security:** CORS is permissive (`*`). For production, restrict origins and consider rate limiting and file size limits.
- **Storage:** No database; processed files live in `app/uploads/`. Filenames are `processed_<original_basename>.jpg` (overwrites on same name).
- **models.py** is empty; no user or session persistence.
- **Root `main.py`** is a stub; real backend entry is `ImageOptimizer.app/run.py`.

---

## 8. Quick Reference

- **Backend port:** 5000  
- **Frontend dev port:** Vite default (e.g. 5173)  
- **Env (frontend):** `VITE_API_URL` in `.env.local`  
- **Accepted image types:** PNG, JPG, JPEG, GIF (both backend and frontend)  
- **Output format:** JPEG only, 50% linear dimensions  

This should be enough for a programmer to navigate the repo, run the app, and extend or fix backend and frontend behavior.
