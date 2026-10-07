import os
import re

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

old_container = '''/* Skiper30 Parallax Gallery */
.parallax-gallery-container {
    position: absolute;
    inset: -20%;
    width: 140%;
    height: 140%;
    z-index: 0;
    pointer-events: none;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-around;
}'''

new_container = '''/* Skiper30 Parallax Gallery */
.parallax-gallery-container {
    position: absolute;
    inset: -20%;
    width: 140%;
    height: 140%;
    z-index: 0;
    pointer-events: none;
    display: block; /* Removed flex to prevent absolute children clumping */
    overflow: hidden;
}'''

css = css.replace(old_container, new_container)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Removed flex from parallax gallery container!")
