from functools import wraps
from flask import Flask, jsonify, request
import pandas as pd
from catBoostApp.model.catboost_model import catboost_model
from datetime import datetime
import os

API_KEY = os.getenv("API_KEY")

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        provided_key = request.headers.get("X-API-Key")
        if not provided_key or provided_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

def parse_value(key, value):
    # Special handling for Age
    if key == "Age":
        if isinstance(value, (int, float)):
            return value

        if isinstance(value, str):
            try:
                if "." in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                pass
            try:
                dob = datetime.strptime(value, "%d/%m/%Y")
                today = datetime.today()
                age = today.year - dob.year - (
                    (today.month, today.day) < (dob.month, dob.day)
                )
                return age
            except ValueError:
                raise ValueError("Age must be numeric or DD/MM/YYYY")

    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass

    return value

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "CatBoost prediction API is running."})


@app.route('/predict', methods=['POST'])
def predict():
    # Expect JSON body
    data = request.get_json()

    rename_map = {
        "Gender": "Sex"
    }

    data = {rename_map.get(k, k): v for k, v in data.items()}

    try:
        data = {k: parse_value(k, v) for k, v in data.items()}
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if data is None:
        return jsonify({"error": "Request must contain JSON"}), 400

    try:
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            return jsonify({"error": "JSON must be a dict or list of dicts"}), 400

        preds = catboost_model.predict(df)
        positive_prob = preds[0][1]

        return jsonify({"Probability of positive sample ": round(float(positive_prob), 4)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
