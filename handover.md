# Smart Gallery - Project Handover

## Project Overview
Smart Gallery is a local, privacy-first photo gallery application that uses AI for scene classification, facial recognition, and semantic search. 
- **Tech Stack:** Python (Flask), SQLite, HTML/JS/CSS (Tailwind, Lucide Icons).
- **Environment:** Runs either as a standard web app (Flask) or wrapped as a native desktop application using `pywebview`.

## Recent Major Architectural Changes
To optimize token usage and reduce codebase bloat, a major architectural consolidation was just completed:
1. **Bridge API Consolidation:** ~800 lines of redundant routing logic were pruned from `app/bridge_api.py`. It now exclusively handles native OS interactions (folder picking, native trash).
2. **Universal Fetch Interception:** `app/static/js/api.js` was stripped of `window.pywebview` fallback checks. All API calls now use standard `fetch()`, which is universally intercepted by `globals.js` and routed to Python via `fetch_internal()` using Flask's test client.

## Recently Completed Features & Fixes
- **Multi-Select Bar:** Fully functional (Add to Album, Copy Photo to Clipboard via Canvas, Archive, Move to Trash).
- **Custom Modals:** Eradicated ugly native browser `alert()` and `confirm()` popups. Replaced with custom async HTML modals (`appAlert` and `appConfirm` in `core.js`).
- **Scan Queue Constraints:** Added a background queue in `app/app_core.py` ensuring only one scan runs at a time. The UI now indicates the queue count.
- **Hero Image Blacklist:** Disliking a hero image now correctly updates the blacklist and instantly syncs with the settings view.
- **Comprehensive Audit Fixes:**
  - **Security:** Patched Zip Slip (unsafe extraction), Path Traversal (in `serve_photo_file`), and SQL Injection (in `ATTACH DATABASE`).
  - **AI & Search:** Fixed `clip_embedding` missing in the DB schema and a crash in `get_text_features` unpacking, restoring Semantic Search functionality.
  - **Clustering:** Fixed a critical logic bug in DBSCAN cluster expansion where processed faces were skipping neighbor discovery.
  - **Performance:** Removed an N+1 query loop in `scan_directory` causing massive slowdowns.

## Current Known Issues / Technical Debt (Pending)
1. **Wildcard Imports:** Many files (like `app.py`, `photos.py`) use `from app.app_core import *`. This was deliberately left untouched during the recent refactor to prevent breaking dependencies, but it causes namespace pollution.
2. **"God Module" (`app_core.py`):** The core file is still ~1300 lines long and handles everything from DB connections to thumbnail generation and EXIF extraction. 
3. **Database Error Swallowing:** Several `try/except Exception: pass` blocks exist across the codebase that silently hide runtime errors.

## Next Steps for New Session
- **Verification:** Ensure the app runs smoothly after the aggressive `bridge_api.py` refactor.
- **Feature Dev:** Address any new user requests regarding search, UI improvements, or the remaining audit items (e.g., adding SQLite FTS5 for text search instead of the expensive Python UDF fuzzy matching).

**To start the app natively:** Run `Start Smart Gallery.bat` or `python run_native.py`.
