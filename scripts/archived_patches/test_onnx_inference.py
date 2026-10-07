import onnxruntime as ort
import numpy as np
from transformers import CLIPProcessor
from huggingface_hub import hf_hub_download
import time

try:
    processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
    
    print("Downloading vision model...")
    vision_path = hf_hub_download(repo_id="Xenova/clip-vit-base-patch32", filename="onnx/vision_model_quantized.onnx")
    print("Downloading text model...")
    text_path = hf_hub_download(repo_id="Xenova/clip-vit-base-patch32", filename="onnx/text_model_quantized.onnx")
    
    print("Loading sessions...")
    vision_session = ort.InferenceSession(vision_path, providers=['CPUExecutionProvider'])
    text_session = ort.InferenceSession(text_path, providers=['CPUExecutionProvider'])
    
    print("Testing text...")
    inputs = processor(text=["a photo of a cat"], return_tensors="np")
    text_inputs = {
        "input_ids": inputs["input_ids"].astype(np.int64),
        "attention_mask": inputs["attention_mask"].astype(np.int64)
    }
    t0 = time.time()
    text_outputs = text_session.run(None, text_inputs)
    print("Text out shape:", text_outputs[0].shape, "Time:", time.time() - t0)
    
    print("Testing vision...")
    # dummy image
    img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    inputs = processor(images=img, return_tensors="np")
    vision_inputs = {
        "pixel_values": inputs["pixel_values"].astype(np.float32)
    }
    t0 = time.time()
    vision_outputs = vision_session.run(None, vision_inputs)
    print("Vision out shape:", vision_outputs[0].shape, "Time:", time.time() - t0)

except Exception as e:
    import traceback
    traceback.print_exc()
