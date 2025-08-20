from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from paddleocr import PaddleOCR
import cv2
import numpy as np
from PIL import Image
import io
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PaddleOCR FastAPI Service",
    description="A FastAPI service for text recognition using PaddleOCR",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PaddleOCR
try:
    ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    logger.info("PaddleOCR initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize PaddleOCR: {e}")
    ocr = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "PaddleOCR FastAPI Service is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "paddleocr_initialized": ocr is not None
    }

@app.post("/ocr/upload")
async def ocr_upload(file: UploadFile = File(...)):
    """
    Extract text from uploaded image file
    """
    if not ocr:
        raise HTTPException(status_code=500, detail="PaddleOCR not initialized")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert PIL image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Perform OCR
        result = ocr.ocr(opencv_image, cls=True)
        
        # Process results
        extracted_text = []
        if result and result[0]:
            for line in result[0]:
                if line:
                    text = line[1][0]  # Extract text from result
                    confidence = line[1][1]  # Extract confidence score
                    bbox = line[0]  # Extract bounding box coordinates
                    
                    extracted_text.append({
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": bbox
                    })
        
        return {
            "success": True,
            "filename": file.filename,
            "text_count": len(extracted_text),
            "results": extracted_text
        }
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/ocr/base64")
async def ocr_base64(image_data: dict):
    """
    Extract text from base64 encoded image
    """
    if not ocr:
        raise HTTPException(status_code=500, detail="PaddleOCR not initialized")
    
    try:
        # Extract base64 data
        base64_string = image_data.get("image")
        if not base64_string:
            raise HTTPException(status_code=400, detail="Base64 image data is required")
        
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to image
        image_bytes = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Perform OCR
        result = ocr.ocr(opencv_image, cls=True)
        
        # Process results
        extracted_text = []
        if result and result[0]:
            for line in result[0]:
                if line:
                    text = line[1][0]
                    confidence = line[1][1]
                    bbox = line[0]
                    
                    extracted_text.append({
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": bbox
                    })
        
        return {
            "success": True,
            "text_count": len(extracted_text),
            "results": extracted_text
        }
        
    except Exception as e:
        logger.error(f"Error processing base64 image: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing base64 image: {str(e)}")

@app.get("/ocr/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "supported_languages": [
            "en", "ch", "chinese_cht", "ko", "ja", "latin", "arabic", "cyrillic"
        ],
        "current_language": "en"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
