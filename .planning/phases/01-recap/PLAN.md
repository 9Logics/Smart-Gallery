# Phase 1: Smart Gallery Story Mode / Recap Feature

## Objective
Build an immersive, dynamic "Story Mode / Recap" feature for Smart Gallery. It shifts the user from "management mode" to a cinematic, highly personalized experience combining Apple-like fluidity with a dynamic, procedurally generated visual aesthetic.

## 1. The Trigger & The "Wipe"
- **UI Trigger**: Start by clicking a specific Year or Month card in the recap dashboard.
- **Transition (FLIP Animation)**: When clicked, the selected card seamlessly expands, taking over the entire window, instantly transitioning the user into the immersive playback canvas.

## 2. The Preloader
- **Skiper15 Loading**: A 3D box loading animation with perspective transforms and smooth rotations takes the stage while the backend intelligently curates the stats.

## 3. The Hook & The Stats
- **Opening Comment**: Automatically starts with a dynamically generated AI comment (e.g., "This year was a wild ride! You saved 450 memories.") customized to the actual data of that year.
- **Stats Roll-up (Skiper37)**: Implement `Number Flow` mechanics (slot-machine style vertical digit scrolling) to present total photos and videos.
- **Top Person & Iconic Place**: Highlights the person you photographed most and an iconic visited location. The iconic place features a physical polaroid card with an animated bouncing `📍` sticker.

## 4. The Dynamic Backdrop (Procedural Themes + Parallax)
- **Yearly Seeded Themes**: Each year is used as a mathematical seed to generate a unique background theme. The engine randomly selects from multiple color palettes and 3 distinct styles:
  - **Gooey Paint Mixing**: Large floating blobs reacting with `feColorMatrix` SVG filters.
  - **Soft Gradient Orbs**: Massive blurred orbs mixing `mix-blend-mode: screen`.
  - **Sharp Geometric Confetti**: Triangles, circles, and rounded squares spinning and cascading across the screen.
- **Skiper30 Parallax Gallery**: A backdrop containing a gallery of up to 5 random photos from that year, floating and parallaxing at different speeds and scales.

## 5. Layered 3D Depth (Skiper29 & Skiper19)
- **Siena Depth (Skiper29)**: The slides and text elements exist in 3D space (`transform-style: preserve-3d`). Mouse movement dynamically tilts the canvas and applies `translateZ` to elements to create physical depth between layers.
- **LinePath (Skiper19)**: An SVG line autonomously drawing itself in the background via `stroke-dashoffset` animations.

## Next Steps / Future Iterations
- Integrate contextual Emojis based on backend AI tags (bouncing across depth layers).
- Apply holographic `border-trail` highlights to Hero moments.
- Integrate the automated staggered entrance scrapbook montage (Skiper79 style) for photo exploration within the recap.
