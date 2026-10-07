import os

plan_path = '.planning/phases/01-recap/PLAN.md'
with open(plan_path, 'r', encoding='utf-8') as f:
    plan = f.read()

# Add typography details
typography_section = '''
## 6. Scrapbook Typography & Styling
- **Handwritten & Cutout Fonts**: Integrate authentic scrapbook-style typography (e.g., marker fonts like `Permanent Marker` or journal fonts like `Caveat`) to replace sterile sans-serifs in key story text.
- **Physical Text Elements**: Apply slight rotations to text elements (like sticker labels or cutout letters) to make them feel physically pasted onto the screen.
- **Mixed Media Feel**: Combine chunky Y2K display fonts for numbers with handwritten annotations for AI comments and place names.
'''

if 'Scrapbook Typography' not in plan:
    plan += typography_section
    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write(plan)
    print("Updated PLAN.md with typography section!")
