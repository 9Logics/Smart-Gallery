# Phase 1: Smart Gallery Story Mode / Recap Feature

## Objective
Build an immersive, dynamic "Story Mode / Recap" feature for Smart Gallery. It shifts the user from "management mode" to a cinematic, highly personalized experience combining Apple-like fluidity with a playful, Y2K-inspired scrapbook aesthetic.

## 1. The Trigger & The "Wipe"
- **UI Trigger**: Implement a subtle, breathing gradient aura and low-profile chevron at the bottom of the home page.
- **Transition**: When triggered, scale down and heavily blur the main photo grid (receding in 3D space) while sliding up a dark, cinematic canvas.

## 2. The Hook
- **Stats Roll-up**: Implement an odometer-style `text-roll` counting up metrics (`124 Photos`, `3 Cities`) using chunky, retro Y2K typography.
- **Title Reveal**: Animate the story title (e.g., "Summer 2026 Vibes") using `Skiper68`-style text reveals.

## 3. The Scrapbook Montage
- **Montage Logic**: Use an automated variation of the `Skiper79` scroll effect.
- **Staggered Entrance**: Photos fly onto the screen sequentially via `animated-group`.
- **Physicality**: Apply randomized, slight rotations (e.g., -4° to +7°) to photos to mimic physical polaroids.

## 4. Y2K Aesthetic & 3D Parallax Emoji Layers
- **Context-Aware Emojis**: Spawn emojis based on AI tags (e.g., 🌊 for beach, 🪩 for party).
- **Depth & Parallax**: Distribute emojis across Foreground (large/blurred/fast), Midground (standard), and Background (tiny/slow) layers.
- **Animation Paths**: Emojis spin, bounce, and drift along bezier paths.
- **Holographic Stickers**: Overlay Y2K-style stickers with a shimmering CSS gradient on photos.

## 5. The Hero Moment
- **Highlighting**: Pause the montage on an AI-selected highlight photo.
- **Cinematic Framing**: Wrap the photo edge with a glowing, comet-like `border-trail`.
- **Interactive 3D**: Apply the `tilt` effect to the Hero photo so it (and its stickers/emojis) pivots in 3D space based on mouse/device movement.
