import sys
sys.path.append('.')
from app.scene_classifier import load_clip, get_image_tags, is_valid_welcome_scene, check_hero_scene, get_text_embedding
import numpy as np

print("Testing load_clip...")
load_clip()

print("Testing get_text_embedding...")
emb = get_text_embedding("a dog")
print("Text emb shape:", emb.shape if emb is not None else None)

# Make a dummy image
from PIL import Image
img = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
img.save("dummy.jpg")

print("Testing get_image_tags...")
tags, img_emb = get_image_tags("dummy.jpg")
print("Tags:", tags)
print("Img emb shape:", img_emb.shape if img_emb is not None else None)

print("Testing is_valid_welcome_scene...")
is_valid = is_valid_welcome_scene("dummy.jpg")
print("Is valid scene:", is_valid)
