import re

# PATCH memories.js
with open('app/static/js/views/memories.js', 'r', encoding='utf-8') as f:
    mem_js = f.read()

target_mem = """        const thumbUrl = `/api/photo/thumbnail/${encodeURIComponent(safePath)}`;
        
        const performSwap = () => {"""

replacement_mem = """        const thumbUrl = `/api/photo/thumbnail/${encodeURIComponent(safePath)}`;
        
        if (item.date_taken || item.created_at || item.date) {
            const d = new Date(item.date_taken || item.created_at || item.date);
            if (!isNaN(d)) {
                subtitle.innerText = d.getFullYear().toString();
            }
        }
        
        const performSwap = () => {"""

if target_mem in mem_js:
    mem_js = mem_js.replace(target_mem, replacement_mem)
    with open('app/static/js/views/memories.js', 'w', encoding='utf-8') as f:
        f.write(mem_js)
    print("Patched memories.js")
else:
    print("Could not find target in memories.js")

# PATCH story_viewer.js
with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    story_js = f.read()

target_story = """      // Text overlays
      const tTitle = document.getElementById('story-bar-title');
      if (tTitle) tTitle.innerText = card.title || '';
      const tSub = document.getElementById('story-top-subtitle');
      if (tSub) tSub.innerText = card.subtitle || '';
      
      const dDate = new Date(photo.date_taken || photo.created_at);
      const tDate = document.getElementById('story-date-text');
      if (tDate) {
          if (!isNaN(dDate)) {
              tDate.innerText = dDate.toLocaleDateString(undefined, { year: 'numeric', month: '2-digit', day: '2-digit' });
          } else {
              tDate.innerText = '';
          }
      }
      
      const hTitle = document.getElementById('story-title');
      const hSub = document.getElementById('story-subtitle');
      if (hTitle) hTitle.innerText = card.title || '';
      if (hSub) hSub.innerText = card.subtitle || '';"""

replacement_story = """      // Text overlays
      const tTitle = document.getElementById('story-bar-title');
      if (tTitle) tTitle.innerText = card.title || '';
      
      const dDate = new Date(photo.date_taken || photo.created_at);
      
      const tSub = document.getElementById('story-top-subtitle');
      if (tSub) {
          if (!isNaN(dDate)) {
              tSub.innerText = dDate.getFullYear().toString();
          } else {
              tSub.innerText = card.subtitle || '';
          }
      }
      
      const tDate = document.getElementById('story-date-text');
      if (tDate) {
          tDate.innerText = ''; // Clear full date
      }
      
      const hTitle = document.getElementById('story-title');
      const hSub = document.getElementById('story-subtitle');
      if (hTitle) hTitle.innerText = card.title || '';
      if (hSub) {
          if (!isNaN(dDate)) {
              hSub.innerText = dDate.getFullYear().toString();
          } else {
              hSub.innerText = card.subtitle || '';
          }
      }"""

if target_story in story_js:
    story_js = story_js.replace(target_story, replacement_story)
    with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
        f.write(story_js)
    print("Patched story_viewer.js")
else:
    print("Could not find target in story_viewer.js")
