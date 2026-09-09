import os
import json
import threading
import traceback
import numpy as np
import cv2
from PIL import Image

# Initialize lazily
clip_model = None
clip_processor = None
device = None
_clip_load_lock = threading.Lock()
_hero_cache_lock = threading.Lock()

# Must be absolute. When this was the relative literal '.cache', the scene cache
# was read and written relative to the process working directory, so it pointed at
# a different file than the absolute CACHE_DIR that app_core, the backup/export
# routines and "delete all data" operate on.
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(
    __file__))), '.cache')
hero_cache_FILE = os.path.join(CACHE_DIR, 'hero_cache.json')

if os.path.exists(hero_cache_FILE):
    try:
        with open(hero_cache_FILE, 'r') as f:
            hero_cache = json.load(f)
        if not isinstance(hero_cache, dict):
            hero_cache = {}
    except Exception:
        hero_cache = {}
else:
    hero_cache = {}

def save_hero_cache():
    """Persist the scene cache atomically.

    The previous version opened the real file with mode 'w' (truncating it) and
    then serialized a dict that background scan threads mutate concurrently. A
    "dictionary changed size during iteration" error mid-dump left a truncated,
    unparseable file behind, and the bare `except: pass` hid it - the whole AI
    classification cache would silently reset on next launch.
    """
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with _hero_cache_lock:
            snapshot = dict(hero_cache)
        tmp_path = hero_cache_FILE + '.tmp'
        with open(tmp_path, 'w') as f:
            json.dump(snapshot, f)
        os.replace(tmp_path, hero_cache_FILE)
    except Exception as e:
        print(f'Failed to save scene cache: {e}')

# Comprehensive list of tags specifically tailored for a photo gallery
GALLERY_TAGS = [
    "cat", "dog", "pet", "bird", "fish", "horse", "wild animal",
    "mountain", "beach", "ocean", "lake", "forest", "tree", "flower", "plant", 
    "sunset", "sunrise", "snow", "winter", "summer", "sky", "cloud", "landscape",
    "city", "building", "house", "indoor", "outdoor", "street", "bridge", 
    "room", "furniture", "bed", "chair", "table", "window",
    "concert", "stadium", "party", "wedding", "crowd", "stage", "performance",
    "poster", "placard", "graffiti", "glasses", "sunglasses", "car", "motorcycle", 
    "bicycle", "boat", "airplane", "train", "vehicle", "book", "document", "text", 
    "screenshot", "sign", "screen", "phone", "computer", "laptop", "camera",
    "food", "drink", "coffee", "meal", "fruit", "vegetable", "dessert", "cake", "restaurant",
    "selfie", "group photo", "portrait", "child", "baby"
]

def load_clip():
    global clip_model, clip_processor, device
    if clip_model is not None:
        return
    # Without this lock the startup preload thread and the first request thread
    # both see clip_model is None and each load a full copy of CLIP (~600MB).
    with _clip_load_lock:
        if clip_model is not None:
            return
        import torch
        from transformers import CLIPProcessor, CLIPModel
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading CLIP AI Model on {device}...")
        model_id = "openai/clip-vit-base-patch32"
        model = CLIPModel.from_pretrained(model_id).to(device)
        processor = CLIPProcessor.from_pretrained(model_id)
        # Publish only once both objects are fully built, so another thread can
        # never observe a non-None model alongside a None processor.
        clip_processor = processor
        clip_model = model
        print("CLIP Model Loaded!")

def unload_clip():
    global clip_model, clip_processor
    clip_model = None
    clip_processor = None
    import gc
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except:
        pass
    print("CLIP Model Unloaded!")

def is_valid_welcome_scene(image_path):
    # Skip video files entirely
    video_exts = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.hevc', '.wmv', '.flv')
    if image_path.lower().endswith(video_exts):
        return False
        
    try:
        img = cv2.imread(image_path)
        if img is None:
            # Fallback to PIL for HEIC/HEIF
            try:
                from PIL import Image
                from pillow_heif import register_heif_opener
                register_heif_opener()
                with Image.open(image_path) as pil_img:
                    pil_img = pil_img.convert('RGB')
                    img = np.array(pil_img)
                    img = img[:, :, ::-1].copy()
            except Exception:
                pass
                
        if img is None:
            return False
            
        # --- AESTHETICS (Blur, Contrast, Brightness) ---
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Blur
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 150.0:
            return False
            
        # 2. Brightness & Contrast
        mean_brightness = np.mean(gray)
        std_contrast = np.std(gray)
        
        if mean_brightness < 40 or mean_brightness > 230:
            return False
        if std_contrast < 30:
            return False

        # If it passes basic aesthetics, check with CLIP
        load_clip()
        
        # Convert BGR back to RGB for PIL
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img_rgb)
        
        # We want to detect if it's a good scenic photo without any people
        scene_tags = [
            "beautiful landscape", "breathtaking scenery", "stunning nature",
            "blurry photo", "boring photo", "document", "screenshot",
            "person", "people", "selfie", "group of people", "man", "woman", "child", "face", "human",
            "indoor room", "close up object", "food", "animal", "pet", "car", "city street"
        ]
        
        import torch
        inputs = clip_processor(text=scene_tags, images=pil_image, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = clip_model(**inputs)
            
        probs = outputs.logits_per_image.softmax(dim=1)[0].cpu().numpy()
        
        # Define bad tags (general rejection) and person tags (strict rejection)
        bad_tags = ["blurry photo", "boring photo", "document", "screenshot", "indoor room", "close up object", "food"]
        person_tags = ["person", "people", "selfie", "group of people", "man", "woman", "child", "face", "human"]
        
        bad_indices = [scene_tags.index(t) for t in bad_tags]
        person_indices = [scene_tags.index(t) for t in person_tags]
        
        best_idx = np.argmax(probs)
        
        # Reject if the absolute best match is a general bad tag
        if best_idx in bad_indices:
            return False
            
        # Reject strictly if there is any reasonable probability (> 5%) of a person being in the photo
        person_prob = sum(probs[i] for i in person_indices)
        if person_prob > 0.05:
            return False
            
        return True
    except Exception as e:
        traceback.print_exc()
        return False

def get_image_tags(image_path, top_k=5):
    """Returns (tags, embedding). Always a 2-tuple - the early-exit paths used to
    return 3-tuples, which would raise ValueError at the unpacking site."""
    video_exts = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.hevc', '.wmv', '.flv')
    if image_path.lower().endswith(video_exts) or not os.path.exists(image_path):
        return [], None
        
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
        pil_image = Image.open(image_path).convert('RGB')
        
        load_clip()
        import torch
        
        # We format tags as "a photo of a {tag}" for better CLIP accuracy
        text_queries = [f"a photo of a {tag}" for tag in GALLERY_TAGS]
        
        inputs = clip_processor(text=text_queries, images=pil_image, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = clip_model(**inputs)
            
        # We can use sigmoid on the logits or softmax. Softmax over 80 classes works well.
        probs = outputs.logits_per_image.softmax(dim=1)[0].cpu().numpy()
        
        # Extract the 512-dim normalized image embedding directly from the main forward pass (already normalized)
        image_embeds = outputs.image_embeds
        embedding_array = image_embeds[0].cpu().detach().numpy().astype(np.float32)
        
        # Get top K tags
        top_indices = np.argsort(probs)[::-1][:top_k]
        
        detected_tags = []
        for i in top_indices:
            # We only keep tags with a reasonable probability threshold (e.g., > 3% in a 80-class softmax)
            if probs[i] > 0.03:
                detected_tags.append(GALLERY_TAGS[i])
                
        return detected_tags, embedding_array
    except Exception as e:
        print(f"Error tagging {image_path}: {e}")
        return [], None

def get_text_embedding(query):
    try:
        load_clip()
        import torch
        inputs = clip_processor(text=[query], images=None, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            text_outputs = clip_model.get_text_features(**inputs)
            text_embeds = text_outputs / text_outputs.norm(p=2, dim=-1, keepdim=True)
        return text_embeds[0].cpu().numpy().astype(np.float32)
    except Exception as e:
        print(f"Error getting text embedding: {e}")
        return None

def check_hero_scene(image_path):
    return is_valid_welcome_scene(image_path)

def semantic_search(query, db_cursor, threshold=0.24, top_k=50):
    """Always returns a list of paths. The failure paths used to return the
    3-tuple ([], None, None), so `for p in semantic_search(...)` would silently
    iterate the tuple instead of a result list."""
    try:
        text_emb = get_text_embedding(query)
        if text_emb is None:
            return []

        db_cursor.execute('SELECT path, clip_embedding FROM photos WHERE clip_embedding IS NOT NULL')
        rows = db_cursor.fetchall()

        if not rows:
            return []

        paths = []
        embeddings = []
        for r in rows:
            paths.append(r[0])
            embeddings.append(np.frombuffer(r[1], dtype=np.float32))

        embeddings_matrix = np.vstack(embeddings)
        # Cosine similarity (embeddings are pre-normalized)
        similarities = np.dot(embeddings_matrix, text_emb)

        # Filter and sort
        results = []
        for i in range(len(similarities)):
            if similarities[i] > threshold:
                results.append((paths[i], similarities[i]))

        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:top_k]]
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return []

