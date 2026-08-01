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
- **Thumbnail Caching**
- **Server-Side API Cache**
- **Client-Side Session Cache**
- **Lazy Loading**
- **Low Graphics Mode**

### 📱 Progressive Web App
- Installable + offline capable

---

## 🛠️ Tech Stack
*(unchanged — keep yours as is)*

---

## 🚀 Getting Started
*(unchanged — your version is already correct)*

---

## 📁 Project Structure
*(unchanged)*

---

## 🗄️ Database Schema
*(unchanged)*

---

## 🤖 AI Models
*(unchanged)*

---

## ⌨️ Keyboard Shortcuts
*(unchanged)*

---

## 📄 License
*(unchanged)*

---

<div align="center">

**Built with ❤️ for photographers who value privacy and local-first software.**

</div>
