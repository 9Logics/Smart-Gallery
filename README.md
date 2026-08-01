<div align="center">

# 📸 Smart Gallery

**A self-hosted, Google Photos-style gallery for your local photo and video library.**

Built with Python + Flask · AI-Powered Face & Scene Recognition · Zero Cloud Dependencies

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-yellow.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)

</div>

---

## ✨ Features

### 🖼️ Photo & Video Management
- **Unified Timeline** — Browse your entire photo & video library in a single, scrollable grid sorted by date
- **Multi-Format Support** — JPG, JPEG, PNG, HEIC/HEIF, WEBP, MP4, MOV, M4V, HEVC, AVI, MKV, WEBM, and more
- **Favorites** — Star your best photos for quick access
- **Archive** — Hide photos from your main feed without deleting them
- **Trash & Recovery** — Soft-delete with full restore capability; permanent purge when ready
- **Bulk Operations** — Select multiple photos to trash, archive, or add to albums at once
- **Duplicate Detection** — Finds duplicate files via perceptual hashing and lets you resolve them in a side-by-side comparison view
- **File Copy** — Copy photos to a new location directly from the app

### 🔍 Search & Filtering
- **Smart Search** — Search by people, places, dates, filenames, or file types with autocomplete suggestions
- **Advanced Filters** — Filter by person, place, album, media type, year, and month — all combinable
- **Date Navigation** — Scroll-linked date badge shows your position in the timeline as you browse
- **Sort Options** — Sort by date (newest/oldest first), filename, or file size

### 🧑‍🤝‍🧑 People & Face Recognition
- **AI Face Detection** — Automatic face detection using OpenCV's YuNet ONNX model
- **Face Recognition & Clustering** — Generates 128-dimensional face embeddings with SFace for automatic grouping of the same person across photos
- **Name Tagging** — Assign names to detected people; the AI learns to cluster similar faces together
- **Manual Face Tagging** — Draw a box on any photo to manually tag a face the AI missed
- **Video Face Detection** — Extract faces from video keyframes
- **People Merge** — Merge duplicate person entries when the AI creates separate clusters for the same person
- **Cover Face Selection** — Choose which photo represents each person in the People grid
- **Training Pairs** — View face similarity pairs to evaluate and fine-tune clustering accuracy

### 🗺️ Places & Maps
- **Automatic Geocoding** — Reads GPS coordinates from EXIF data and reverse-geocodes them into human-readable place names
- **Smart Location Grouping** — Clusters nearby GPS coordinates into logical place groups with configurable thresholds
- **Interactive Map** — View photo locations on a Leaflet.js-powered map with clickable markers
- **Place Cards** — Browse places as visual cards with AI-prioritized scenic thumbnails
- **Map Data View** — See all geotagged photos plotted on a single world map

### 📁 Albums
- **Custom Albums** — Create, rename, and delete albums
- **Add/Remove Photos** — Add single or multiple photos to any album
- **Album Covers** — Set a custom cover photo for each album
- **Album Detail View** — Browse photos within an album in a dedicated grid

### 🧠 AI & Scene Classification
- **Scene Recognition** — MobileNetV2 ONNX model classifies photos as landscapes, nature, animals, flowers, and more
- **Blur Detection** — Laplacian variance analysis automatically filters out blurry photos from hero backgrounds
- **Welcome Hero** — AI-curated scenic slideshow on the home page, prioritizing high-quality photos from 2020+
- **Smart Caching** — Scene classification results are cached to JSON for instant subsequent lookups

### 🎞️ Memories
- **Welcome Hero Slideshow** — Cinematic crossfading hero banner with your best scenic photos
- **On This Day** — Photos taken on today's date in previous years
- **Spotlight on a Day** — AI-curated highlight of a standout day from your library
- **Featured Moment** — A single standout photo picked by the curation algorithm
- **Video Spotlight** — A featured video from your collection
- **Album Pick** — A random album showcased with its cover photo
- **People Spotlight** — Highlights a named person with their photo count, shared photos, and a carousel

### 📊 Statistics Dashboard
- **Library Overview** — Total photos, videos, and storage breakdown
- **Yearly & Monthly Charts** — Interactive bar/line charts showing photo & video counts over time
- **Storage Analysis** — Track how much disk space photos vs. videos consume per year/month
- **Activity Heatmap** — GitHub-style contribution heatmap showing your photo-taking frequency
- **Calendar View** — Full calendar visualization of daily photo counts

### 🔧 Metadata & Editing
- **EXIF Viewer** — View resolution, file size, camera make/model, f-stop, exposure time, focal length, and ISO
- **Date & Time Editing** — Edit photo dates with a scroll-wheel date picker or raw input, with AM/PM support
- **Filename Renaming** — Rename files directly from the info panel
- **Fix Date from Filename** — Automatically extract and set the date from common filename patterns (e.g., `20231225_143022.jpg`)
- **GPS Coordinate Editing** — Manually set or correct latitude/longitude with live map preview
- **Open in System** — Open the photo in your OS default viewer or reveal it in File Explorer
- **Metadata Refresh** — Re-read EXIF data from disk for individual photos or the entire library

### 🔄 Scanning & Maintenance
- **Directory Scanning** — Point the app at any folder and it recursively indexes all photos and videos
- **Background Processing** — Scanning, face detection, and geocoding run in background threads
- **Scan Status** — Real-time progress indicator in the sidebar
- **Cache Rebuild** — Regenerate all thumbnails from scratch
- **Missing File Detection** — Find and clean up database entries for files that no longer exist on disk
- **Safe Face Rescan** — Re-detect faces without losing your named person groups

### ⚡ Performance
- **Thumbnail Caching** — Generates and caches 300px thumbnails for instant grid loading
- **Server-Side API Cache** — In-memory response caching with automatic invalidation on mutations
- **Client-Side Session Cache** — Browser `sessionStorage` caching of API responses for instant navigation
- **Lazy Hero Loading** — First hero image loads instantly; remaining images load progressively in the background
- **Low Graphics Mode** — Toggle to disable animations for better performance on slower machines

### 📱 Progressive Web App
- **Installable** — Add to your home screen on mobile or desktop via the PWA manifest
- **Standalone Mode** — Runs in its own window without browser chrome
- **Service Worker** — Offline-capable with static asset caching

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, Flask 3.0 |
| **Database** | SQLite (zero-config, file-based) |
| **Frontend** | Vanilla HTML/CSS/JS, Lucide Icons, Google Fonts (Inter, Outfit) |
| **Face Detection** | OpenCV DNN — YuNet ONNX |
| **Face Recognition** | OpenCV DNN — SFace ONNX |
| **Scene Classification** | OpenCV DNN — MobileNetV2 ONNX |
| **Image Processing** | Pillow, pillow-heif, OpenCV |
| **Maps** | Leaflet.js + OpenStreetMap |
| **PWA** | Service Worker + Web App Manifest |

All AI models are downloaded automatically on first run. **No API keys, no cloud services, no subscriptions.**

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** — https://www.python.org/downloads/
- **Windows** — Currently optimized for Windows (Linux/macOS may work with minor tweaks)

### Quick Start (Windows)

The easiest way to get started is to double-click the setup script:

```
setup.bat
```

This will automatically:
1. Create a Python virtual environment (`.venv`)
2. Install all dependencies from `requirements.txt`
3. Start the Flask server
4. Open the app at **http://127.0.0.1:5000**

### Manual Setup

```bash
# Clone the repository
git clone https://github.com/9Logics/Smart-Gallery.git
cd Smart-Gallery

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

### First-Time Setup

1. Navigate to **Settings** in the sidebar
2. Set your **Scan Folder** — the root directory containing your photos and videos
3. Click **Scan Directory** — the app will recursively index all supported media files
4. Face detection, geocoding, and scene classification will run automatically in the background

---

## 📁 Project Structure

```
Smart-Gallery/
├── app.py                    # Flask backend — all API routes & business logic
├── face_processor.py         # YuNet face detection + SFace recognition
├── scene_classifier.py       # MobileNetV2 scene classification + blur detection
├── setup.bat                 # One-click Windows setup script
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT License
│
├── templates/
│   └── index.html            # Single-page application HTML
│
├── static/
│   ├── style.css             # All application styles
│   ├── manifest.json         # PWA manifest
│   ├── sw.js                 # Service worker
│   ├── icons/                # PWA icons (192px, 512px)
│   ├── images/               # Default hero background images
│   └── js/
│       ├── core.js           # Main application logic, state, and event handling
│       └── views/
│           ├── memories.js   # Welcome hero + memories carousel
│           ├── photos.js     # Photo grid rendering & virtual scrolling
│           ├── albums.js     # Album management UI
│           ├── people.js     # People grid & face management
│           ├── places.js     # Places cards & map integration
│           ├── duplicates.js # Duplicate detection & resolution UI
│           ├── stats.js      # Statistics dashboard & charts
│           └── trash.js      # Trash management UI
│
└── .cache/                   # Auto-generated (gitignored)
    ├── gallery.db            # SQLite database
    ├── thumbnails/           # Cached 300px thumbnails
    ├── scene_cache.json      # Scene classification results
    └── models/               # Auto-downloaded ONNX models
        ├── face_detection_yunet_2023mar.onnx
        ├── face_recognition_sface_2021dec.onnx
        ├── mobilenetv2-7.onnx
        └── imagenet_classes.txt
```

---

## 🗄️ Database Schema

Smart Gallery uses SQLite with the following tables:

| Table | Purpose |
|-------|---------|
| `photos` | Core photo/video metadata — path, date, dimensions, GPS, EXIF camera info, hash |
| `faces` | Detected face bounding boxes and 128-D embeddings, linked to photos and people |
| `people` | Named person identities with cover face references |
| `albums` | User-created albums with cover photos |
| `album_photos` | Many-to-many junction between albums and photos |
| `geocoding_cache` | Cached reverse geocoding results to avoid redundant API calls |
| `settings` | Key-value store for app configuration (scan folder, etc.) |

---

## 🤖 AI Models

All models run **locally** via OpenCV's DNN module — no internet required after first download.

| Model | Purpose | Size |
|-------|---------|------|
| **YuNet** | Face detection — locates faces in photos and video frames | ~230 KB |
| **SFace** | Face recognition — generates 128-D embeddings for clustering | ~37 MB |
| **MobileNetV2** | Scene classification — identifies landscapes, animals, flowers | ~14 MB |

Models are automatically downloaded from GitHub on first launch and cached in `.cache/models/`.

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `←` / `→` | Navigate between photos in lightbox |
| `Escape` | Close lightbox or modal |
| `Delete` | Trash the current photo |
| `F` | Toggle favorite |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Copyright © 2026 [9Logics](https://github.com/9Logics)

---

<div align="center">

**Built with ❤️ for photographers who value privacy and local-first software.**

</div>

