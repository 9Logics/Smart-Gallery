import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

target = '''                    } else {
                        progressEl.style.width = count + '%';
                    }
                }, 100);
            }
        }
    </script>'''

replacement = '''                    } else {
                        progressEl.style.width = count + '%';
                    }
                }, 100);
            } else {
                document.getElementById('recap-container').classList.remove('options-active');
                document.getElementById('rewind-dashboard').classList.remove('active');
                const preloader = document.getElementById('pixel-preloader');
                if (preloader) {
                    preloader.style.opacity = '0';
                    setTimeout(() => preloader.style.display = 'none', 500);
                }
            }
        }
    </script>'''

html = html.replace(target, replacement)
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Added else block to toggleRecap")
