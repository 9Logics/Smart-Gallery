import os

FILE = "app/scene_classifier.py"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Replace imports
code = code.replace(
'''        import torch
        from transformers import CLIPProcessor, CLIPModel
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading CLIP AI Model on {device}...")
        model_id = "openai/clip-vit-base-patch32"
        model = CLIPModel.from_pretrained(model_id).to(device)
        processor = CLIPProcessor.from_pretrained(model_id)''',
'''        import onnxruntime as ort
        from transformers import CLIPProcessor
        from huggingface_hub import hf_hub_download
        print("Loading ONNX CLIP AI Model...")
        model_id = "openai/clip-vit-base-patch32"
        processor = CLIPProcessor.from_pretrained(model_id)
        
        vision_path = hf_hub_download(repo_id="Xenova/clip-vit-base-patch32", filename="onnx/vision_model_quantized.onnx")
        text_path = hf_hub_download(repo_id="Xenova/clip-vit-base-patch32", filename="onnx/text_model_quantized.onnx")
        
        vision_session = ort.InferenceSession(vision_path, providers=['CPUExecutionProvider'])
        text_session = ort.InferenceSession(text_path, providers=['CPUExecutionProvider'])
        model = {"vision": vision_session, "text": text_session}
        device = "cpu"'''
)

code = code.replace(
'''    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except:
        pass''',
'''    pass'''
)

# is_valid_welcome_scene
code = code.replace(
'''        import torch
        inputs = clip_processor(text=scene_tags, images=pil_image, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = clip_model(**inputs)
            
        probs = outputs.logits_per_image.softmax(dim=1)[0].cpu().numpy()''',
'''        inputs = clip_processor(text=scene_tags, images=pil_image, return_tensors="np", padding=True)
        text_inputs = {"input_ids": inputs["input_ids"].astype(np.int64)}
        vision_inputs = {"pixel_values": inputs["pixel_values"].astype(np.float32)}
        
        text_embeds = clip_model["text"].run(None, text_inputs)[0]
        image_embeds = clip_model["vision"].run(None, vision_inputs)[0]
        
        text_embeds = text_embeds / np.linalg.norm(text_embeds, axis=-1, keepdims=True)
        image_embeds = image_embeds / np.linalg.norm(image_embeds, axis=-1, keepdims=True)
        
        logits_per_image = 100.0 * np.dot(image_embeds, text_embeds.T)
        exp_logits = np.exp(logits_per_image - np.max(logits_per_image, axis=1, keepdims=True))
        probs = (exp_logits / np.sum(exp_logits, axis=1, keepdims=True))[0]'''
)

# get_image_tags
code = code.replace(
'''        import torch
        
        # We format tags as "a photo of a {tag}" for better CLIP accuracy
        text_queries = [f"a photo of a {tag}" for tag in GALLERY_TAGS]
        
        inputs = clip_processor(text=text_queries, images=pil_image, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = clip_model(**inputs)
            
        # We can use sigmoid on the logits or softmax. Softmax over 80 classes works well.
        probs = outputs.logits_per_image.softmax(dim=1)[0].cpu().numpy()
        
        # Extract the 512-dim normalized image embedding directly from the main forward pass (already normalized)
        image_embeds = outputs.image_embeds
        embedding_array = image_embeds[0].cpu().detach().numpy().astype(np.float32)''',
'''        text_queries = [f"a photo of a {tag}" for tag in GALLERY_TAGS]
        
        inputs = clip_processor(text=text_queries, images=pil_image, return_tensors="np", padding=True)
        text_inputs = {"input_ids": inputs["input_ids"].astype(np.int64)}
        vision_inputs = {"pixel_values": inputs["pixel_values"].astype(np.float32)}
        
        text_embeds = clip_model["text"].run(None, text_inputs)[0]
        image_embeds = clip_model["vision"].run(None, vision_inputs)[0]
        
        text_embeds = text_embeds / np.linalg.norm(text_embeds, axis=-1, keepdims=True)
        image_embeds = image_embeds / np.linalg.norm(image_embeds, axis=-1, keepdims=True)
        
        logits_per_image = 100.0 * np.dot(image_embeds, text_embeds.T)
        exp_logits = np.exp(logits_per_image - np.max(logits_per_image, axis=1, keepdims=True))
        probs = (exp_logits / np.sum(exp_logits, axis=1, keepdims=True))[0]
        
        embedding_array = image_embeds[0].astype(np.float32)'''
)

# get_text_embedding
code = code.replace(
'''        import torch
        inputs = clip_processor(text=[query], images=None, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            text_outputs = clip_model.get_text_features(**inputs)
            text_embeds = text_outputs / text_outputs.norm(p=2, dim=-1, keepdim=True)
        return text_embeds[0].cpu().numpy().astype(np.float32)''',
'''        inputs = clip_processor(text=[query], images=None, return_tensors="np", padding=True)
        text_inputs = {"input_ids": inputs["input_ids"].astype(np.int64)}
        
        text_outputs = clip_model["text"].run(None, text_inputs)[0]
        text_embeds = text_outputs / np.linalg.norm(text_outputs, axis=-1, keepdims=True)
        return text_embeds[0].astype(np.float32)'''
)

# get_image_tags_batch
code = code.replace(
'''        import torch
        text_queries = [f"a photo of a {tag}" for tag in GALLERY_TAGS]
        
        inputs = clip_processor(text=text_queries, images=valid_images, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = clip_model(**inputs)
            
        probs = outputs.logits_per_image.softmax(dim=1).cpu().numpy()
        image_embeds = outputs.image_embeds
        embedding_array = image_embeds.cpu().detach().numpy().astype(np.float32)''',
'''        text_queries = [f"a photo of a {tag}" for tag in GALLERY_TAGS]
        
        inputs = clip_processor(text=text_queries, images=valid_images, return_tensors="np", padding=True)
        text_inputs = {"input_ids": inputs["input_ids"].astype(np.int64)}
        vision_inputs = {"pixel_values": inputs["pixel_values"].astype(np.float32)}
        
        text_embeds = clip_model["text"].run(None, text_inputs)[0]
        image_embeds = clip_model["vision"].run(None, vision_inputs)[0]
        
        text_embeds = text_embeds / np.linalg.norm(text_embeds, axis=-1, keepdims=True)
        image_embeds = image_embeds / np.linalg.norm(image_embeds, axis=-1, keepdims=True)
        
        logits_per_image = 100.0 * np.dot(image_embeds, text_embeds.T)
        exp_logits = np.exp(logits_per_image - np.max(logits_per_image, axis=1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
        
        embedding_array = image_embeds.astype(np.float32)'''
)


# check_hero_scene_batch
code = code.replace(
'''        import torch
        
        scene_tags = [
            "beautiful landscape", "breathtaking scenery", "stunning nature",
            "blurry photo", "boring photo", "document", "screenshot",
            "person", "people", "selfie", "group of people", "man", "woman", "child", "face", "human",
            "indoor room", "close up object", "food", "animal", "pet", "car", "city street"
        ]
        
        inputs = clip_processor(text=scene_tags, images=valid_images, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = clip_model(**inputs)
            
        probs = outputs.logits_per_image.softmax(dim=1).cpu().numpy()''',
'''        scene_tags = [
            "beautiful landscape", "breathtaking scenery", "stunning nature",
            "blurry photo", "boring photo", "document", "screenshot",
            "person", "people", "selfie", "group of people", "man", "woman", "child", "face", "human",
            "indoor room", "close up object", "food", "animal", "pet", "car", "city street"
        ]
        
        inputs = clip_processor(text=scene_tags, images=valid_images, return_tensors="np", padding=True)
        text_inputs = {"input_ids": inputs["input_ids"].astype(np.int64)}
        vision_inputs = {"pixel_values": inputs["pixel_values"].astype(np.float32)}
        
        text_embeds = clip_model["text"].run(None, text_inputs)[0]
        image_embeds = clip_model["vision"].run(None, vision_inputs)[0]
        
        text_embeds = text_embeds / np.linalg.norm(text_embeds, axis=-1, keepdims=True)
        image_embeds = image_embeds / np.linalg.norm(image_embeds, axis=-1, keepdims=True)
        
        logits_per_image = 100.0 * np.dot(image_embeds, text_embeds.T)
        exp_logits = np.exp(logits_per_image - np.max(logits_per_image, axis=1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)'''
)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch applied successfully.")
