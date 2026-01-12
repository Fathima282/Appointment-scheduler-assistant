from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import dateutil.parser
import pytz
import pytesseract
from PIL import Image
import io
import re

# Configure Tesseract path (CHANGE THIS to your installation path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
CORS(app)

# Timezone
IST = pytz.timezone('Asia/Kolkata')

# Helper function to get current date in IST
def get_current_date():
    return datetime.now(IST)

# Step 1: OCR/Text Extraction
@app.route('/api/ocr', methods=['POST'])
def ocr_extraction():
    try:
        # Check if image file is provided
        if 'image' in request.files:
            image_file = request.files['image']
            image = Image.open(io.BytesIO(image_file.read()))
            raw_text = pytesseract.image_to_string(image)
            confidence = 0.75  # OCR confidence (simulated)
        # Check if text is provided
        elif 'text' in request.json:
            raw_text = request.json['text']
            confidence = 0.90
        else:
            return jsonify({"error": "No text or image provided"}), 400
        
        return jsonify({
            "raw_text": raw_text.strip(),
            "confidence": confidence
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Step 2: Entity Extraction
@app.route('/api/extract', methods=['POST'])
def entity_extraction():
    try:
        raw_text = request.json.get('raw_text', '')
        
        # Extract date phrase
        date_patterns = [
            r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'tomorrow',
            r'today',
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}'
        ]
        
        date_phrase = None
        for pattern in date_patterns:
            match = re.search(pattern, raw_text.lower())
            if match:
                date_phrase = match.group()
                break
        
        # Extract time phrase
        time_match = re.search(r'\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?', raw_text)
        time_phrase = time_match.group() if time_match else None
        
        # Extract department
        departments = ['dentist', 'cardiology', 'orthopedic', 'pediatric', 'general']
        department = None
        for dept in departments:
            if dept in raw_text.lower():
                department = dept
                break
        
        if not date_phrase or not time_phrase or not department:
            return jsonify({
                "status": "needs_clarification",
                "message": "Ambiguous date/time or department"
            }), 400
        
        return jsonify({
            "entities": {
                "date_phrase": date_phrase,
                "time_phrase": time_phrase,
                "department": department
            },
            "entities_confidence": 0.85
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Step 3: Normalization
@app.route('/api/normalize', methods=['POST'])
def normalization():
    try:
        entities = request.json.get('entities', {})
        date_phrase = entities.get('date_phrase', '').lower()
        time_phrase = entities.get('time_phrase', '')
        
        current_date = get_current_date()
        
        # Parse date phrase
        if 'tomorrow' in date_phrase:
            target_date = current_date + timedelta(days=1)
        elif 'today' in date_phrase:
            target_date = current_date
        elif 'next' in date_phrase:
            # Find the next occurrence of the day
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for i, day in enumerate(days):
                if day in date_phrase:
                    days_ahead = i - current_date.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                    target_date = current_date + timedelta(days=days_ahead)
                    break
        else:
            # Try to parse as date
            try:
                target_date = dateutil.parser.parse(date_phrase, fuzzy=True)
                target_date = IST.localize(target_date)
            except:
                return jsonify({
                    "status": "needs_clarification",
                    "message": "Could not parse date"
                }), 400
        
        # Parse time phrase
        time_phrase_clean = time_phrase.strip()
        
        # Handle various time formats
        if 'pm' in time_phrase_clean.lower() or 'am' in time_phrase_clean.lower():
            time_obj = dateutil.parser.parse(time_phrase_clean).time()
        else:
            # Assume 24-hour format or convert based on context
            hour = int(re.search(r'\d{1,2}', time_phrase_clean).group())
            if hour < 12 and hour >= 1:
                # Could be PM, but we'll assume PM for afternoon appointments
                hour_24 = hour + 12 if hour < 12 else hour
            else:
                hour_24 = hour
            time_obj = datetime.strptime(f"{hour_24}:00", "%H:%M").time()
        
        return jsonify({
            "normalized": {
                "date": target_date.strftime("%Y-%m-%d"),
                "time": time_obj.strftime("%H:%M"),
                "tz": "Asia/Kolkata"
            },
            "normalization_confidence": 0.90
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Step 4: Final Appointment JSON
@app.route('/api/appointment', methods=['POST'])
def final_appointment():
    try:
        entities = request.json.get('entities', {})
        normalized = request.json.get('normalized', {})
        
        department_map = {
            'dentist': 'Dentistry',
            'cardiology': 'Cardiology',
            'orthopedic': 'Orthopedics',
            'pediatric': 'Pediatrics',
            'general': 'General Medicine'
        }
        
        department = entities.get('department', '')
        department_formal = department_map.get(department, department.title())
        
        return jsonify({
            "appointment": {
                "department": department_formal,
                "date": normalized.get('date'),
                "time": normalized.get('time'),
                "tz": normalized.get('tz')
            },
            "status": "ok"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Appointment Scheduler API is running",
        "endpoints": [
            "/api/ocr",
            "/api/extract",
            "/api/normalize",
            "/api/appointment"
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)