from flask import Flask, render_template, request, jsonify
import cv2
import pandas as pd
from ultralytics import YOLO
from collections import Counter
import os
import base64
import numpy as np

app = Flask(__name__)

model = YOLO('yolov8m.pt')

def load_prices():
    if os.path.exists('dataset.csv'):
        df = pd.read_csv('dataset.csv')
        df.columns = df.columns.str.strip()
        return {str(k).lower().strip(): v for k, v in zip(df.item, df.price)}
    return {}

def process_image_and_get_bill(img):
    results = model.predict(img, conf=0.25)
    result = results[0]
    detected_list = [result.names[int(box.cls[0])] for box in result.boxes]
    counts = Counter(detected_list)
    prices = load_prices()
    
    bill_data = []
    total = 0.0
    for item, qty in counts.items():
        item_key = item.lower().strip()
        if item_key in prices:
            unit_price = float(prices[item_key])
            sub = unit_price * qty
            total += sub
            bill_data.append({
                "name": item.title(),
                "qty": qty, 
                "unit": f"₹{unit_price:.2f}", 
                "sub": f"₹{sub:.2f}"
            })

    _, buffer = cv2.imencode('.jpg', result.plot())
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    
    return {
        "annotated_image": "data:image/jpeg;base64," + encoded_image,
        "bill": bill_data,
        "total": f"₹{total:,.2f}"
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan_frame', methods=['POST'])
def scan_frame():
    try:
        data = request.json['image']
        encoded_data = data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return jsonify(process_image_and_get_bill(img))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scan', methods=['POST'])
def scan():
    try:
        file = request.files['file']
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return jsonify(process_image_and_get_bill(img))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)