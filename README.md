# AI-Powered Appointment Scheduler

Backend service that parses natural language appointment requests and converts them into structured scheduling data.

## Features
- OCR text extraction from images
- Natural language entity extraction
- Date/time normalization to Asia/Kolkata timezone
- Structured JSON output
- Error handling and guardrails

## Setup Instructions

### Prerequisites
- Python 3.8+
- Tesseract OCR

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/appointment-scheduler.git
cd appointment-scheduler
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR:
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Update path in app.py line 12

5. Run the application:
```bash
python app.py
```

The API will be available at http://localhost:5000

## API Endpoints

### 1. OCR/Text Extraction
`POST /api/ocr`

**Request (Text):**
```json
{
  "text": "Book dentist next Friday at 3pm"
}
```

**Request (Image):**
```
Form-data: image file
```

**Response:**
```json
{
  "raw_text": "Book dentist next Friday at 3pm",
  "confidence": 0.90
}
```

### 2. Entity Extraction
`POST /api/extract`

**Request:**
```json
{
  "raw_text": "Book dentist next Friday at 3pm"
}
```

**Response:**
```json
{
  "entities": {
    "date_phrase": "next Friday",
    "time_phrase": "3pm",
    "department": "dentist"
  },
  "entities_confidence": 0.85
}
```

### 3. Normalization
`POST /api/normalize`

**Request:**
```json
{
  "entities": {
    "date_phrase": "next Friday",
    "time_phrase": "3pm",
    "department": "dentist"
  }
}
```

**Response:**
```json
{
  "normalized": {
    "date": "2025-01-17",
    "time": "15:00",
    "tz": "Asia/Kolkata"
  },
  "normalization_confidence": 0.90
}
```

### 4. Final Appointment
`POST /api/appointment`

**Request:**
```json
{
  "entities": {
    "department": "dentist"
  },
  "normalized": {
    "date": "2025-01-17",
    "time": "15:00",
    "tz": "Asia/Kolkata"
  }
}
```

**Response:**
```json
{
  "appointment": {
    "department": "Dentistry",
    "date": "2025-01-17",
    "time": "15:00",
    "tz": "Asia/Kolkata"
  },
  "status": "ok"
}
```

## Testing

Use the provided curl commands in `test_requests.txt` or import the Postman collection.

## Architecture
```
Input (Text/Image)
      ↓
[OCR/Text Extraction] → Extract raw text
      ↓
[Entity Extraction] → Identify date, time, department
      ↓
[Normalization] → Convert to ISO format (Asia/Kolkata)
      ↓
[Final Output] → Structured appointment JSON
```

## Error Handling

The API includes guardrails for:
- Missing or ambiguous dates/times
- Invalid departments
- OCR failures
- Malformed requests

## Author

[Your Name]
```

✅ **Save with `Ctrl + S`**

---

### **Step 16: Create requirements.txt**

1. **"File"** → **"New File"**
2. Save as: `requirements.txt`
3. Copy and paste:
```
Flask==3.0.0
flask-cors==4.0.0
python-dateutil==2.8.2
pytz==2023.3
pytesseract==0.3.10
Pillow==10.1.0
```

✅ **Save**

---

### **Step 17: Create .gitignore**

1. **"File"** → **"New File"**
2. Save as: `.gitignore`
3. Copy and paste:
```
venv/
__pycache__/
*.pyc
.env
.DS_Store