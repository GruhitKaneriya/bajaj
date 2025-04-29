import re
import os
import cv2
import numpy as np
import pytesseract
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class LabTest:
    test_name: str
    value: str
    unit: Optional[str] = None
    bio_reference_range: Optional[str] = None
    lab_test_out_of_range: Optional[bool] = None
    
    def to_dict(self):
        return {
            'test_name': self.test_name,
            'value': self.value,
            'unit': self.unit,
            'bio_reference_range': self.bio_reference_range,
            'lab_test_out_of_range': self.lab_test_out_of_range
        }

def preprocess_image(image_path: str) -> np.ndarray:
    """Preprocess image to improve OCR accuracy"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image {image_path}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text(image_path: str, config: str = '--psm 6 --oem 3') -> str:
    """Extract text from an image using OCR"""
    preprocessed = preprocess_image(image_path)
    text = pytesseract.image_to_string(preprocessed, config=config)
    return text.strip()

def is_value_out_of_range(value: str, range_text: str) -> bool:
    """Determine if the test value is outside the reference range"""
    if not range_text:
        return False
    
    try:
        numeric_value = re.search(r'([\d.]+)', value)
        if not numeric_value:
            return False
        
        numeric_value = float(numeric_value.group(1))
        
        # Range patterns
        range_match = re.search(r'([\d.]+)[\s-]+to[\s-]+([\d.]+)|(\d+\.?\d*)[\s-]*-[\s-]*(\d+\.?\d*)', range_text)
        if range_match:
            lower = float(range_match.group(1)) if range_match.group(1) else float(range_match.group(3))
            upper = float(range_match.group(2)) if range_match.group(2) else float(range_match.group(4))
            return numeric_value < lower or numeric_value > upper
            
        less_than_match = re.search(r'<\s*([\d.]+)', range_text)
        if less_than_match:
            return numeric_value >= float(less_than_match.group(1))
            
        greater_than_match = re.search(r'>\s*([\d.]+)', range_text)
        if greater_than_match:
            return numeric_value <= float(greater_than_match.group(1))
        
        return False
    except Exception:
        return False

def extract_unit(value_text: str) -> Tuple[str, Optional[str]]:
    """Extract value and unit from combined text"""
    unit_patterns = [
        r'(\d+\.?\d*)\s*(\w+/%|/cumm|/mm3|mill/cumm|mill/mm3|g/dL|gm/dL|gm%|mg/L|mg/dL|pg|pgm|fL|%|U/L|mIU/L)',
        r'(\d+\.?\d*)\s*\[?[HL]?\]?\s*(\w+/%|/cumm|/mm3|mill/cumm|mill/mm3|g/dL|gm/dL|gm%|mg/L|mg/dL|pg|pgm|fL|%|U/L|mIU/L)'
    ]
    
    for pattern in unit_patterns:
        match = re.search(pattern, value_text)
        if match:
            return match.group(1), match.group(2)
    
    value_only = re.search(r'(\d+\.?\d*)\s*\[?[HL]?\]?', value_text)
    return (value_only.group(0), None) if value_only else (value_text, None)

def parse_lab_report(text: str) -> List[LabTest]:
    """Parse extracted text to identify lab tests"""
    lab_tests = []
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for i, line in enumerate(lines):
        if any(x in line.lower() for x in ['report', 'end of', 'laboratory', 'patient', 'doctor', 'sample']):
            continue
            
        # Pattern 1: Test: Value Unit Range
        if ':' in line:
            parts = line.split(':')
            if len(parts) >= 2:
                test_name = parts[0].strip()
                value_unit = parts[1].strip()
                
                ref_range = None
                if i + 1 < len(lines) and re.search(r'[\d.]+[\s-]+(to|-)[\s-]+[\d.]+', lines[i+1]):
                    ref_range = lines[i+1].strip()
                elif re.search(r'[\d.]+[\s-]+(to|-)[\s-]+[\d.]+', value_unit):
                    range_match = re.search(r'([\d.]+[\s-]+(to|-)[\s-]+[\d.]+)', value_unit)
                    ref_range = range_match.group(0)
                    value_unit = value_unit.replace(ref_range, '').strip()
                
                value, unit = extract_unit(value_unit)
                if test_name and value and ref_range:
                    lab_tests.append(LabTest(
                        test_name=test_name,
                        value=value,
                        unit=unit,
                        bio_reference_range=ref_range,
                        lab_test_out_of_range=is_value_out_of_range(value, ref_range)
                    ))
    
    return [test for test in lab_tests if test.bio_reference_range is not None]