import os

file_path = 'app/scene_classifier.py'
with open(file_path, 'r', encoding='utf-8') as f:
    src = f.read()

batch_func = """
def get_image_tags_batch(image_paths, top_k=5):
    video_exts = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.hevc', '.wmv', '.flv')
    results = [([], None)] * len(image_paths)
    valid_indices = []
    valid_images = []
    
    from pillow_heif import register_heif_opener
    register_heif_opener()
    
    for i, path in enumerate(image_paths):
        if path.lower().endswith(video_exts) or not os.path.exists(path):
            continue
        try:
            pil_image = Image.open(path).convert('RGB')
            valid_images.append(pil_image)
            valid_indices.append(i)
        except:
            pass
            
    if not valid_images:
        return results
        
    try:
        load_clip()
        import torch
        text_queries = [f"a photo of a {tag}" for tag in GALLERY_TAGS]
        
        inputs = clip_processor(text=text_queries, images=valid_images, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = clip_model(**inputs)
            
        probs = outputs.logits_per_image.softmax(dim=1).cpu().numpy()
        image_embeds = outputs.image_embeds
        embedding_array = image_embeds.cpu().detach().numpy().astype(np.float32)
        
        for idx, orig_i in enumerate(valid_indices):
            p = probs[idx]
            top_indices = np.argsort(p)[::-1][:top_k]
            detected_tags = []
            for j in top_indices:
                if p[j] > 0.03:
                    detected_tags.append(GALLERY_TAGS[j])
            results[orig_i] = (detected_tags, embedding_array[idx])
            
        return results
    except Exception as e:
        print(f"Error in batch tagging: {e}")
        return results

def check_hero_scene_batch(image_paths):
    video_exts = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.hevc', '.wmv', '.flv')
    results = [False] * len(image_paths)
    valid_indices = []
    valid_images = []
    
    for i, path in enumerate(image_paths):
        if path.lower().endswith(video_exts) or not os.path.exists(path):
            continue
            
        try:
            img = cv2.imread(path)
            if img is None:
                try:
                    from PIL import Image
                    from pillow_heif import register_heif_opener
                    register_heif_opener()
                    with Image.open(path) as pil_img:
                        pil_img = pil_img.convert('RGB')
                        img = np.array(pil_img)
                        img = img[:, :, ::-1].copy()
                except:
                    pass
            if img is None:
                continue
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 150.0:
                continue
                
            mean_brightness = np.mean(gray)
            std_contrast = np.std(gray)
            if mean_brightness < 40 or mean_brightness > 230:
                continue
            if std_contrast < 30:
                continue
                
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(img_rgb)
            valid_images.append(pil_image)
            valid_indices.append(i)
        except:
            pass
            
    if not valid_images:
        return results
        
    try:
        load_clip()
        import torch
        
        scene_tags = [
            "beautiful landscape", "breathtaking scenery", "stunning nature",
            "blurry photo", "boring photo", "document", "screenshot",
            "person", "people", "selfie", "group of people", "man", "woman", "child", "face", "human",
            "indoor room", "close up object", "food", "animal", "pet", "car", "city street"
        ]
        
        inputs = clip_processor(text=scene_tags, images=valid_images, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = clip_model(**inputs)
            
        probs = outputs.logits_per_image.softmax(dim=1).cpu().numpy()
        
        bad_tags = ["blurry photo", "boring photo", "document", "screenshot", "indoor room", "close up object", "food"]
        person_tags = ["person", "people", "selfie", "group of people", "man", "woman", "child", "face", "human"]
        
        bad_indices = [scene_tags.index(t) for t in bad_tags]
        person_indices = [scene_tags.index(t) for t in person_tags]
        
        for idx, orig_i in enumerate(valid_indices):
            p = probs[idx]
            best_idx = np.argmax(p)
            if best_idx in bad_indices:
                continue
            person_prob = sum(p[j] for j in person_indices)
            if person_prob > 0.05:
                continue
            results[orig_i] = True
            
        return results
    except Exception as e:
        print(f"Error in batch hero check: {e}")
        return results
"""

if "def get_image_tags_batch" not in src:
    src += "\n" + batch_func
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(src)
    print("scene_classifier.py patched.")
