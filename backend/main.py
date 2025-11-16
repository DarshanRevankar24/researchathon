from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import logging
from fastapi.middleware.cors import CORSMiddleware

from processors.image_processor import image_processor
from processors.video_processor import video_processor
from processors.text_processor import text_processor

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------
# FASTAPI SETUP
# -----------------------------------------------------------
app = FastAPI(
    title="Explainable Deepfake Detection API",
    description="Image, Video & Text AI-generated content detection",
    version="1.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # ⚠️ In production set allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------
# MODELS
# -----------------------------------------------------------
class TextRequest(BaseModel):
    text: str

class DetectionResponse(BaseModel):
    prediction: str
    confidence: float
    is_fake: bool
    explanations: Dict[str, Any]

# -----------------------------------------------------------
# STARTUP LOAD MODELS
# -----------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Initializing all models...")

    # Load IMAGE model
    image_processor.load_model("models/image_detector.pth")

    # Load VIDEO model — uses same CNN model
    video_processor.load_model("models/image_detector.pth")

    # Load TEXT model
    text_processor.load_model("models/text_detector.pth")

    logger.info("✅ All models initialized successfully.")

# -----------------------------------------------------------
# HEALTH CHECK
# -----------------------------------------------------------
@app.get("/health")
async def health_check():
    return {"status": "healthy", "models_loaded": True}

# -----------------------------------------------------------
# IMAGE DETECTION
# -----------------------------------------------------------
@app.post("/detect/image", response_model=DetectionResponse)
async def detect_image(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image (PNG or JPG)")
        
        image_bytes = await file.read()
        tensor = image_processor.preprocess_image(image_bytes)

        prediction = image_processor.predict(tensor)
        explanations = image_processor.generate_explanations(tensor)

        return DetectionResponse(
            prediction=prediction["prediction"],
            confidence=prediction["confidence"],
            is_fake=prediction["is_fake"],
            explanations=explanations
        )

    except Exception as e:
        logger.error(f"Image detection error: {str(e)}")
        raise HTTPException(500, f"Image processing error: {str(e)}")

# -----------------------------------------------------------
# VIDEO DETECTION
# -----------------------------------------------------------
@app.post("/detect/video")
async def detect_video(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv','.gif')):
            raise HTTPException(400, "File must be a video (MP4, MOV, AVI, MKV,GIF)")

        video_bytes = await file.read()

        response = video_processor.process_video(video_bytes)

        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Video detection error: {str(e)}")
        raise HTTPException(500, f"Video processing error: {str(e)}")

# -----------------------------------------------------------
# TEXT DETECTION
# -----------------------------------------------------------
@app.post("/detect/text", response_model=DetectionResponse)
async def detect_text(request: TextRequest):
    try:
        text = request.text.strip()

        if len(text) < 10:
            raise HTTPException(400, "Text must be at least 10 characters")

        tensor = text_processor.preprocess_text(text)
        prediction = text_processor.predict(tensor)
        explanations = text_processor.generate_explanations(text, tensor)

        return DetectionResponse(
            prediction=prediction["prediction"],
            confidence=prediction["confidence"],
            is_fake=prediction["is_fake"],
            explanations=explanations
        )

    except Exception as e:
        logger.error(f"Text detection error: {str(e)}")
        raise HTTPException(500, f"Text processing error: {str(e)}")

# -----------------------------------------------------------
# MAIN SERVER RUN
# -----------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
