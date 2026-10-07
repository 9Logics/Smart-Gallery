path = 'app/static/style.css'
with open(path, 'r', encoding='utf-8') as f:
    css = f.read()

target = """.rewind-mini-card {
    position: relative;
    width: 220px;
    height: 140px;
    background: linear-gradient(135deg, #1c1c1e, #050505); /* Base color */
    flex-shrink: 0;
    border-radius: 20px;
    overflow: hidden;
    cursor: pointer;
    scroll-snap-align: start;
    
}"""

replacement = """.rewind-mini-card {
    position: relative;
    width: 220px;
    height: 140px;
    background: linear-gradient(135deg, #1c1c1e, #050505); /* Base color */
    flex-shrink: 0;
    border-radius: 20px;
    overflow: hidden;
    cursor: pointer;
    scroll-snap-align: start;
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s ease;
}"""

css = css.replace(target, replacement)

target_hero = """.rewind-hero-card {
    position: relative;
    width: 100%;
    height: 380px; /* Much taller to eliminate negative space */
    background: linear-gradient(135deg, #2c2c2e, #1c1c1e);
    border-radius: 24px;
    overflow: hidden;
    cursor: pointer;
    margin-bottom: 30px; /* Gap before horizontal scroller */
    
}"""

replacement_hero = """.rewind-hero-card {
    position: relative;
    width: 100%;
    height: 380px; /* Much taller to eliminate negative space */
    background: linear-gradient(135deg, #2c2c2e, #1c1c1e);
    border-radius: 24px;
    overflow: hidden;
    cursor: pointer;
    margin-bottom: 30px; /* Gap before horizontal scroller */
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s ease;
}"""

if target_hero in css:
    css = css.replace(target_hero, replacement_hero)

with open(path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Added transitions to cards")
