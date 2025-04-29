# Lab Report Parser API

## Overview

This project is a solution to the **Bajaj Finserv Health – Data Science Q2** problem statement dated **29th April 2025**. The goal is to extract lab test data from lab report images, including:

- Lab test names
- Test values
- Reference ranges
- Flag indicating if the value is out of range

The solution is implemented using Python and deployed as a FastAPI web service.


## Project Structure

- `untitled2.ipynb`:  
  Contains the full solution, including data parsing, visualization, testing, and validation. This notebook showcases the end-to-end functionality along with results.

- `main.py`:  
  FastAPI implementation exposing a `/get-lab-tests` POST endpoint. The endpoint accepts an image file and returns structured lab test data.

- `lab_parser.py`:  
  Core logic for extracting test names, values, and reference ranges from the lab report image.



---



### Endpoint

