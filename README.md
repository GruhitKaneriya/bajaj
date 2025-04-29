# Lab Report Parser API

## Overview

This project is a solution to the **Bajaj Finserv Health – Data Science Q2** problem statement dated **29th April 2025**. The goal is to extract lab test data from lab report images, including:

- Lab test names  
- Test values  
- Reference ranges  
- Flag indicating if the value is out of range  

The solution is implemented using Python and deployed as a FastAPI web service.

---

## Project Structure

- `untitled2.ipynb`:  
  Contains the full solution, including data parsing, visualization, testing, and validation. This notebook showcases the end-to-end functionality along with results.

- `main.py`:  
  FastAPI implementation exposing a `/get-lab-tests` POST endpoint. The endpoint accepts an image file and returns structured lab test data.

- `lab_parser.py`:  
  Core logic for extracting test names, values, and reference ranges from the lab report image.

---

## Sample Parsed Table

| test_name           | value | unit  | bio_reference_range    | lab_test_out_of_range |
|---------------------|-------|-------|-------------------------|------------------------|
| Blood Urea          | 30    | mg/dl | 15-45                   | False                  |
| Creatinine          | 09    | mg/dl | 0.5-1.4                 | True                   |
| Uric Acid           | 6.0   | mg/dl | F -2.4-5.7              | True                   |
| S. Bilirubin        | 07    |       | 0.2-1.2                 | True                   |
| SGOT                | 54    | UA    | 5-46                    | True                   |
| Sodium              | 137.1 | meq/l | 135-155                 | False                  |
| Calcium             | 8.23  | me/dl | 8.4-10.4                | True                   |
| ...                 | ...   | ...   | ...                     | ...                    |

---

## API Response (JSON)

```json
{
  "is_success": true,
  "lab_tests": [
    {
      "test_name": "Blood Urea",
      "value": "30",
      "unit": "mg/dl",
      "bio_reference_range": "15-45",
      "lab_test_out_of_range": false
    },
    {
      "test_name": "Creatinine",
      "value": "09",
      "unit": "mg/dl",
      "bio_reference_range": "0.5-1.4",
      "lab_test_out_of_range": true
    }
    // Additional lab test entries
  ]
}
