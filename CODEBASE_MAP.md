# Smart Gallery Codebase Map

This is a structural guide intended to help AI Agents find features, injection points, and file paths accurately without brittle regex searches.

## 1. Project Root & Core App
- `app/templates/index.html` — The main layout. Contains the structural HTML for the Rewind Dashboard (`#recap-container`) and the Recap Player modal (`#recap-player-overlay`). **Do not put massive inline scripts here. Use the modular JS files.**
- `app/routes/photos.py` — The core backend API. Contains `/api/recap/generate/<year>` which curates the complex data structures (top person, top place, gallery moments) for the recap slideshow.

## 2. JavaScript Engine (`app/static/js/`)
We have modularized the JS to make patching reliable:
- `recap_player.js` — The massive engine driving the immersive slideshow.
  - Look for `// --- [REGION: OPEN & INIT PLAYER] ---` to find the API fetch and DOM injection loop.
  - Look for `// --- [REGION: SLIDE TRANSITION LOGIC] ---` to edit the Skiper-30/32 transitions.
  - Look for `// --- [REGION: CYCLING DECK ENGINE (SKIPER-54)] ---` to edit the physical photo dealing animation.
- `recap_dashboard.js` — The logic for the main dashboard (fetching the years, month counts, and initializing the `.rewind-mini-card`s).
  - Look for `// --- [REGION: DASHBOARD INIT] ---` to patch the async fetch or count badge injections.
- `search.js` — Handlers for the global search bar.
- `selection.js` — Core image gallery selection state and interactions.

## 3. Styles (`app/static/style.css`)
CSS is shared globally.
- `.recap-` prefix: Layouts for the slides.
- `.rewind-` prefix: Layouts for the dashboard memory cards.
- `.siena-` prefix: 3D perspective triggers.
- `.skiper` prefix: specific animation classes reverse-engineered from Skiper UI.

## Golden Rules for AI Agents Editing This Code:
1. **Never use `re.sub()` to replace massive 40-line blocks of Javascript or HTML** unless you anchor your regex perfectly. Use the `// --- [REGION: ...] ---` markers.
2. **Never inject unquoted HTML tags** into JavaScript strings unless you use backticks (template literals).
3. **Always run `node -c <file.js>`** after patching a javascript file via Python to ensure you didn't break the syntax.
