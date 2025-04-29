from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from lab_parser import LabTest, parse_lab_report, extract_text
import cv2
import numpy as np
import os
from typing import List

app = FastAPI(
    title="Bajaj Lab Report Parser API",
    description="API for extracting lab test results from report images",
    version="1.0.0"
)

@app.post("/get-lab-tests", response_model=dict)
async def process_lab_report(file: UploadFile = File(...)):
    try:
        # Read and validate image
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")
        
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Save temporary file for Tesseract
        temp_file = "temp_report.png"
        cv2.imwrite(temp_file, img)
        
        # Process with existing logic
        extracted_text = extract_text(temp_file)
        lab_tests = parse_lab_report(extracted_text)
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return {
            "is_success": True,
            "lab_tests": [test.to_dict() for test in lab_tests]
        }
        
    except Exception as e:
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}