# Phase 1: Project Gallery One Story Mode / Recap Feature

## Objective
Build an immersive, dynamic "Story Mode / Recap" feature for Project Gallery One. It shifts the user from "management mode" to a cinematic, highly personalized experience combining the fluid, advanced animations of Skiper UI (15, 19, 29, 30, 37) with a playful, Y2K-inspired scrapbook aesthetic.

## 1. The Trigger & The Preloader
- **UI Trigger**: Start by clicking a specific Year or Month card in the recap dashboard.
- **Transition (FLIP Animation)**: When clicked, the selected card seamlessly expands, taking over the entire window.
- **Skiper15 Preloader**: A 3D box loading animation with perspective transforms and smooth rotations takes the stage while the backend intelligently curates the stats.

## 2. The Hook
- **Opening Comment & Title**: Automatically starts with a dynamically generated AI comment. Animate the story title (e.g., "Summer 2026 Vibes") using `Skiper68`-style text reveals.
- **Stats Roll-up (Skiper37)**: Implement `Number Flow` mechanics (odometer-style vertical digit scrolling) to present total photos and videos, using chunky, retro Y2K typography.

## 3. The Scrapbook Montage & Dynamic Backdrop
- **Montage Logic**: Use an automated variation of the `Skiper79` scroll effect combined with the **Skiper30 Parallax Gallery**.
- **Staggered Entrance**: Photos fly onto the screen sequentially via `animated-group`.
- **Physicality**: Apply randomized, slight rotations (e.g., -4° to +7°) to photos to mimic physical polaroids.
- **Procedural Themes**: Generate seeded background themes (gooey blobs, soft orbs, sharp confetti) based on the year to compliment the scrapbook feel.

## 4. Y2K Aesthetic & 3D Parallax Emoji Layers
- **Context-Aware Emojis**: Spawn emojis based on AI tags (e.g., 🌊 for beach, 🪩 for party).
- **Depth & Parallax (Skiper29)**: Distribute emojis across Foreground (large/blurred/fast), Midground (standard), and Background (tiny/slow) layers using Siena depth mechanics.
- **Animation Paths**: Emojis spin, bounce, and drift along bezier paths.
- **Holographic Stickers**: Overlay Y2K-style stickers with a shimmering CSS gradient on photos (including the 📍 sticker on the Iconic Place).

## 5. The Hero Moment
- **Highlighting**: Pause the montage on an AI-selected highlight photo (Memorable Moment).
- **Cinematic Framing**: Wrap the photo edge with a glowing, comet-like `border-trail`.
- **Interactive 3D (Skiper29)**: Apply the `tilt` effect to the Hero photo so it (and its stickers/emojis) pivots in 3D space based on mouse/device movement.
- **LinePath (Skiper19)**: An SVG line autonomously drawing itself in the background to anchor the Hero moment.

## 6. Scrapbook Typography & Styling
- **Handwritten & Cutout Fonts**: Integrate authentic scrapbook-style typography (e.g., marker fonts like `Permanent Marker` or journal fonts like `Caveat`) to replace sterile sans-serifs in key story text.
- **Physical Text Elements**: Apply slight rotations to text elements (like sticker labels or cutout letters) to make them feel physically pasted onto the screen.
- **Mixed Media Feel**: Combine chunky Y2K display fonts for numbers with handwritten annotations for AI comments and place names.
