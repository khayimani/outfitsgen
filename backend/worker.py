try:
    import torch
    from PIL import Image
    from transformers import CLIPProcessor, CLIPModel
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("ML dependencies not found. Running in mock mode.")

# Placeholder for ML Worker
class MLWorker:
    def __init__(self):
        self.model_id = "openai/clip-vit-base-patch32"
        # Delay loading to avoid memory usage during init if not needed immediately
        self.model = None
        self.processor = None

    def load_model(self):
        if not ML_AVAILABLE:
            return
            
        if not self.model:
            print("Loading CLIP model...")
            self.model = CLIPModel.from_pretrained(self.model_id)
            self.processor = CLIPProcessor.from_pretrained(self.model_id)
            print("CLIP model loaded.")

    def process_image(self, image_path: str):
        if not ML_AVAILABLE:
            print(f"Mock processing image: {image_path}")
            # Return a random 512-dim vector
            import random
            return [random.random() for _ in range(512)]
            
        self.load_model()
        image = Image.open(image_path)
        inputs = self.processor(text=None, images=image, return_tensors="pt", padding=True)
        img_features = self.model.get_image_features(**inputs)
        return img_features.detach().numpy().flatten().tolist()

worker = MLWorker()
