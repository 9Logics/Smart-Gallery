import re

html_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\templates\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_code = f.read()

cdns = """
    <!-- Phase 1: High-End UI Libraries -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
</head>"""

html_code = html_code.replace("</head>", cdns)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_code)
print("Injected GSAP and Swiper into index.html")
