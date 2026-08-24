import os
import re

def extract_functions(source, function_names):
    extracted = []
    remaining = source
    for name in function_names:
        # Regex to match function definition until the end of its block
        # We find 'function name(' and count braces
        pattern = re.compile(rf"^function\s+{name}\s*\(.*?\)\s*{{", re.MULTILINE)
        match = pattern.search(remaining)
        if not match:
            print(f"Could not find function {name}")
            continue
            
        start_idx = match.start()
        
        # find matching closing brace
        brace_count = 0
        in_string = False
        string_char = ''
        escape = False
        
        end_idx = start_idx
        for i in range(start_idx, len(remaining)):
            char = remaining[i]
            
            if not escape and (char == '"' or char == "'" or char == '`'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif string_char == char:
                    in_string = False
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            
            if char == '\\':
                escape = not escape
            else:
                escape = False
                
        func_code = remaining[start_idx:end_idx]
        extracted.append(func_code)
        remaining = remaining[:start_idx] + remaining[end_idx:]
        
    return '\n\n'.join(extracted), remaining

with open('static/js/core.js', 'r', encoding='utf-8') as f:
    core_js = f.read()

# 1. Modals
modal_funcs = [
    'editFaceTagPrompt', 'closeRetagModal', 'setPersonCoverFace', 'renamePersonPrompt',
    'openVideoPersonModal', 'closeVideoPersonModal', 'openManualFaceModal', 'submitManualFaceLabel',
    'deleteFaceLabel', 'unnamePerson', 'deletePerson', 'openCoverPhotoModal', 
    'openRenameAlbumModal', 'openAlbumCoverModal', 'handleMissingPhoto', 'showDataModal', 'hideDataModal'
]
modals_code, core_js = extract_functions(core_js, modal_funcs)
with open('static/js/ui_modals.js', 'w', encoding='utf-8') as f:
    f.write(modals_code)

# 2. Drawing / Faces manual mode
drawing_funcs = [
    'toggleManualFaceDrawingMode', 'resetDrawingState', 'handleDrawStart', 
    'handleDrawing', 'updateDrawingOverlay', 'handleDrawEnd'
]
drawing_code, core_js = extract_functions(core_js, drawing_funcs)
with open('static/js/ui_drawing.js', 'w', encoding='utf-8') as f:
    f.write(drawing_code)

# 3. AI Training
ai_funcs = ['startAiTraining', 'showNextTrainingPair']
ai_code, core_js = extract_functions(core_js, ai_funcs)
with open('static/js/ai_training.js', 'w', encoding='utf-8') as f:
    f.write(ai_code)

# 4. Stats Heatmap
stats_funcs = ['initStatsHeatmap', 'loadStatsHeatmap']
stats_code, core_js = extract_functions(core_js, stats_funcs)
with open('static/js/views/stats_heatmap.js', 'w', encoding='utf-8') as f:
    f.write(stats_code)

# Save the reduced core.js
with open('static/js/core.js', 'w', encoding='utf-8') as f:
    f.write(core_js)

print("JS Refactoring complete.")
