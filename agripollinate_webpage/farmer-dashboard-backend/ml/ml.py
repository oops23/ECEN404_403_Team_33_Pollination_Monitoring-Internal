from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from ultralytics.nn.tasks import DetectionModel
from PIL import Image
import io
import uvicorn
import torch
import base64

# Add safe globals with the actual class object
torch.serialization.add_safe_globals([DetectionModel])

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load YOLO model 
try:
    model = YOLO("best.pt")
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

@app.get("/")
def root():
    return {"service": "AgriPollinate ML Detection", "status": "running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy" if model else "model_not_loaded",
        "service": "ml-detection",
        "model_loaded": model is not None
    }

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    if not model:
        return {
            "success": False,
            "error": "Model not loaded"
        }
    
    try:
        # Load image
        img_bytes = await file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        # Run YOLO detection
        results = model(img, conf=0.25)[0]
        
        # Generate annotated image in memory
        result_img = results.plot()
        annotated_img = Image.fromarray(result_img)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        annotated_img.save(img_byte_arr, format='JPEG', quality=95)
        img_byte_arr.seek(0)

        # Extract detections
        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            detections.append({
                "class_id": cls_id,
                "class_name": results.names[cls_id],
                "confidence": conf,
                "bbox": xyxy
            })

        # Return JSON with detections and image as base64
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

        return {
            "success": True,
            "detections": detections,
            "total_detections": len(detections),
            "annotated_image_base64": img_base64
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    print("🚀 Starting FastAPI ML Detection Service...")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")