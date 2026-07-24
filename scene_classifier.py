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
                return False
                
            # --- BLUR DETECTION ---
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 150.0:
                # Photo is too blurry
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
            
            # Check if any top label matches our keywords
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
