import os
import urllib.request
import cv2
import numpy as np
import traceback

# Paths
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
MODELS_DIR = os.path.join(CACHE_DIR, "models")
ONNX_PATH = os.path.join(MODELS_DIR, "mobilenetv2-7.onnx")
LABELS_PATH = os.path.join(MODELS_DIR, "imagenet_classes.txt")

# URLs
MODEL_URL = "https://github.com/onnx/models/raw/main/validated/vision/classification/mobilenet/model/mobilenetv2-7.onnx"
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"

# Keywords that indicate nature, flowers, or animals
VALID_KEYWORDS = [
    # Landscapes/Nature
    'mountain', 'valley', 'lakeside', 'seashore', 'promontory', 'forest', 'alp', 
    'cliff', 'reef', 'beach', 'park', 'tree', 'volcano', 'coral', 'sandbar', 'geyser',
    # Flowers
    'flower', 'daisy', 'rose', 'sunflower', 'tulip', 'orchid', 'pot', 'vase',
    # Animals
    'cat', 'dog', 'bird', 'animal', 'lion', 'tiger', 'bear', 'horse', 'deer', 'fox', 'wolf', 
    'elephant', 'monkey', 'panda', 'leopard', 'cheetah', 'penguin', 'dolphin', 'whale',
    'fish', 'butterfly', 'bee', 'rabbit', 'hamster', 'terrier', 'retriever', 'spaniel',
    'hound', 'collie', 'poodle', 'pug', 'tabby', 'husky', 'malamute'
]

# Keywords that indicate humans or people (to strictly reject)
INVALID_KEYWORDS = [
    'person', 'people', 'human', 'man', 'woman', 'child', 'boy', 'girl', 
    'face', 'portrait', 'suit', 'groom', 'bride', 'player', 'crowd', 'audience', 
    'baby', 'toddler', 'teen', 'guy', 'lady', 'gentleman'
]


import json

SCENE_CACHE_FILE = os.path.join(CACHE_DIR, 'scene_cache.json')
if os.path.exists(SCENE_CACHE_FILE):
    try:
        with open(SCENE_CACHE_FILE, 'r') as f:
            scene_cache = json.load(f)
    except:
        scene_cache = {}
else:
    scene_cache = {}

def save_scene_cache():
    try:
        with open(SCENE_CACHE_FILE, 'w') as f:
            json.dump(scene_cache, f)
    except:
        pass

class SceneClassifier:

    def __init__(self):
        self.net = None
        self.classes = []
        self._initialize()
        
    def _initialize(self):
        if not os.path.exists(MODELS_DIR):
            os.makedirs(MODELS_DIR)
            
        if not os.path.exists(ONNX_PATH):
            print("Downloading MobileNet V2 for scene classification...")
            try:
                urllib.request.urlretrieve(MODEL_URL, ONNX_PATH)
            except Exception as e:
                print(f"Failed to download ONNX: {e}")
            
        if not os.path.exists(LABELS_PATH):
            print("Downloading ImageNet labels...")
            try:
                urllib.request.urlretrieve(LABELS_URL, LABELS_PATH)
            except Exception as e:
                print(f"Failed to download labels: {e}")
            
        if os.path.exists(LABELS_PATH):
            with open(LABELS_PATH, "r") as f:
                self.classes = [line.strip().lower() for line in f.readlines()]
            
        if os.path.exists(ONNX_PATH):
            try:
                self.net = cv2.dnn.readNetFromONNX(ONNX_PATH)
            except Exception as e:
                print(f"Error loading Scene Classifier ONNX: {e}")

    def is_valid_welcome_scene(self, image_path):
        if not self.net or not os.path.exists(image_path):
            return False
            
        try:
            img = cv2.imread(image_path)
            if img is None:
                # Fallback to PIL for HEIC/HEIF
                try:
                    from PIL import Image
                    from pillow_heif import register_heif_opener
                    import numpy as np
                    register_heif_opener()
                    with Image.open(image_path) as pil_img:
                        pil_img = pil_img.convert('RGB')
                        img = np.array(pil_img)
                        # Convert RGB to BGR for OpenCV consistency
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
                # Photo is too blurry
                scene_cache[image_path] = False
                save_scene_cache()
                return False
                
            # 2. Brightness & Contrast
            mean_brightness = np.mean(gray)
            std_contrast = np.std(gray)
            
            if mean_brightness < 40 or mean_brightness > 230:
                # Too dark or completely blown out
                scene_cache[image_path] = False
                save_scene_cache()
                return False
                
            if std_contrast < 30:
                # Very low contrast / flat image
                scene_cache[image_path] = False
                save_scene_cache()
                return False
            # ----------------------

            if img is None:
                return False
                
            # MobileNet expects 224x224 RGB image
            blob = cv2.dnn.blobFromImage(img, 1.0/255.0, (224, 224), (0.485, 0.456, 0.406), swapRB=True, crop=False)
            self.net.setInput(blob)
            out = self.net.forward()
            
            scores = out[0]
            top_indices = np.argsort(scores)[::-1][:5]
            
            top_labels = [self.classes[i] for i in top_indices]
            
            # Check for invalid human labels first to aggressively filter them out
            for label in top_labels:
                for keyword in INVALID_KEYWORDS:
                    if keyword in label:
                        return False
            
            # Check if any top label matches our valid keywords
            for label in top_labels:
                for keyword in VALID_KEYWORDS:
                    if keyword in label:
                        return True
                        
            return False
        except Exception as e:
            traceback.print_exc()
            return False

# Global instance
scene_classifier = SceneClassifier()

def check_scene(image_path):
    return scene_classifier.is_valid_welcome_scene(image_path)
