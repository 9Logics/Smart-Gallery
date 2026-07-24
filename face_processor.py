import os
import urllib.request
import cv2
import numpy as np

# Paths
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
MODELS_DIR = os.path.join(CACHE_DIR, "models")
YUNET_PATH = os.path.join(MODELS_DIR, "face_detection_yunet_2023mar.onnx")
SFACE_PATH = os.path.join(MODELS_DIR, "face_recognition_sface_2021dec.onnx")

# URLs
YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/master/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
SFACE_URL = "https://github.com/opencv/opencv_zoo/raw/master/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"

def ensure_models_downloaded():
    """Ensure that the face detection and recognition ONNX models are downloaded."""
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)

    for name, url, path in [("YuNet (Face Detection)", YUNET_URL, YUNET_PATH), 
                            ("SFace (Face Recognition)", SFACE_URL, SFACE_PATH)]:
        if not os.path.exists(path):
            print(f"Downloading {name} model from {url}...")
            try:
                # Use a custom User-Agent to avoid issues with some servers
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
                    data = response.read()
                    out_file.write(data)
                print(f"Downloaded {name} successfully to {path}")
            except Exception as e:
                print(f"Error downloading {name}: {e}")
                raise RuntimeError(f"Could not download face model: {e}. Please check your internet connection.")

class FaceProcessor:
    def __init__(self):
        ensure_models_downloaded()
        # Initialize models
        # Note: input size is placeholder, will be set per image
        self.detector = cv2.FaceDetectorYN.create(YUNET_PATH, "", (320, 320))
        self.recognizer = cv2.FaceRecognizerSF.create(SFACE_PATH, "")

    def detect_and_extract_faces(self, image_path, min_confidence=0.8):
        """
        Detects faces in an image and extracts bounding boxes and embeddings.
        Returns: List of dicts, each containing:
                 'bbox': [x, y, w, h],
                 'embedding': numpy array (128,)
        """
        # Read image
        img = None
        is_video = image_path.lower().endswith(('.mp4', '.mov', '.m4v', '.hevc'))
        
        if is_video:
            try:
                cap = cv2.VideoCapture(image_path)
                if cap.isOpened():
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    target_frame = min(max(10, int(frame_count * 0.1)), frame_count - 1) if frame_count > 10 else 0
                    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        img = frame
                cap.release()
            except Exception as e:
                print(f"Error reading video {image_path}: {e}")
        else:
            try:
                from PIL import Image, ImageOps
                import pillow_heif
                pillow_heif.register_heif_opener()
                
                with Image.open(image_path) as pil_img:
                    # Transpose first to ensure orientation is correct and coordinates match!
                    pil_img = ImageOps.exif_transpose(pil_img)
                    img = cv2.cvtColor(np.array(pil_img.convert('RGB')), cv2.COLOR_RGB2BGR)
            except Exception as e:
                print(f"PIL loading failed for {image_path}: {e}")
                img = cv2.imread(image_path)
            
        if img is None:
            return []

        h, w, _ = img.shape
        
        # Scale down for detection to prevent hallucinations on hi-res images
        max_dim = 1024
        scale = 1.0
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            det_img = cv2.resize(img, (new_w, new_h))
            self.detector.setInputSize((new_w, new_h))
        else:
            det_img = img
            self.detector.setInputSize((w, h))
            
        self.detector.setScoreThreshold(float(min_confidence))
        
        # Detect faces
        _, faces = self.detector.detect(det_img)
        
        results = []
        if faces is not None:
            # Scale coordinates back up
            if scale != 1.0:
                faces[:, 0:14] = faces[:, 0:14] / scale
            for face in faces:
                confidence = face[14]
                if confidence < min_confidence:
                    continue
                
                # Bounding box
                # Extract coordinates
                x, y, width, height = map(int, face[0:4])
                # Keep box within bounds
                x = max(0, x)
                y = max(0, y)
                width = min(w - x, width)
                height = min(h - y, height)
                
                if width <= 0 or height <= 0:
                    continue
                
                try:
                    # Align and crop face
                    aligned_face = self.recognizer.alignCrop(img, face)
                    # Extract embedding
                    embedding = self.recognizer.feature(aligned_face)
                    # Squeeze embedding to shape (128,)
                    embedding = embedding.flatten()
                    
                    results.append({
                        "bbox": [x, y, width, height],
                        "embedding": embedding
                    })
                except Exception as e:
                    print(f"Failed to extract face embedding in {image_path}: {e}")
                    
        return results

def compute_cosine_distance(embedding1, embedding2):
    """Computes cosine distance between two 128-dimensional embeddings."""
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    if norm1 == 0 or norm2 == 0:
        return 1.0
    similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
    return float(1.0 - similarity)

def dbscan_clustering(embeddings, eps=0.45, min_samples=2):
    """
    Standard DBSCAN algorithm implemented in NumPy to group faces.
    embeddings: List or array of shape (N, 128)
    eps: Cosine distance threshold (tightened to 0.45 to prevent chaining)
    min_samples: Minimum number of samples to form a cluster
    Returns: numpy array of labels (N,) where -1 is noise, and 0..K-1 are cluster IDs.
    """
    n_samples = len(embeddings)
    if n_samples == 0:
        return np.array([], dtype=int)
    
    embeddings = np.array(embeddings, dtype=np.float32)
    
    # Compute pairwise distance matrix (cosine distance)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    normalized = embeddings / norms
    
    similarity = np.dot(normalized, normalized.T)
    dist_matrix = 1.0 - similarity
    
    labels = -np.ones(n_samples, dtype=int)
    cluster_id = 0
    
    for i in range(n_samples):
        if labels[i] != -1:
            continue
            
        # Find neighbors within eps distance
        neighbors = np.where(dist_matrix[i] < eps)[0]
        if len(neighbors) < min_samples:
            continue
            
        # Start new cluster
        labels[i] = cluster_id
        
        # Expand cluster
        queue = list(neighbors)
        while len(queue) > 0:
            current = queue.pop(0)
            if labels[current] == -1: # Was noise, now assigned
                labels[current] = cluster_id
            elif labels[current] != -1: # Already processed
                continue
                
            labels[current] = cluster_id
            
            # Find neighbors of current point
            current_neighbors = np.where(dist_matrix[current] < eps)[0]
            if len(current_neighbors) >= min_samples:
                # Add unvisited neighbors
                for n in current_neighbors:
                    if labels[n] == -1:
                        queue.append(n)
                        
        cluster_id += 1
        
    return labels
