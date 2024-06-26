from flask import Flask, request, jsonify, abort
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import logging
import base64
from functools import wraps

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# API Key for authentication
API_KEY = os.getenv('MY_API_KEY')
app.logger.debug(f"Loaded API Key: {API_KEY}")

# Google Sheets Configuration
def get_google_sheet(sheet_name):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_path = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_SECRET')
        if not creds_path:
            app.logger.error("Google Sheets service account secret not found. Make sure GOOGLE_SHEETS_SERVICE_ACCOUNT_SECRET is set.")
            return None
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open(f"{sheet_name}").sheet1
        app.logger.info(f"Successfully accessed Google Sheet: {sheet_name}")
        return sheet
    except gspread.exceptions.SpreadsheetNotFound:
        app.logger.error("Spreadsheet not found. Please check the name '{sheet_name}}'.")
        return None
    except gspread.exceptions.APIError as api_err:
        app.logger.error(f"Google API error: {api_err}")
        return None
    except Exception as e:
        app.logger.error(f"An unexpected error occurred while accessing Google Sheet: {e}")
        return None

# Decorator to require API key via Basic Auth
def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        app.logger.debug(f"Authorization header received: {auth_header}")
        if auth_header:
            auth_type, credentials = auth_header.split()
            if auth_type == 'Basic':
                decoded_credentials = base64.b64decode(credentials).decode('utf-8')
                app.logger.debug(f"Decoded credentials: {decoded_credentials}")
                try:
                    api_key, dummy = decoded_credentials.split(':')
                    app.logger.debug(f"Received API Key: {api_key}")
                except ValueError:
                    app.logger.warning("Invalid credentials format.")
                    abort(401)
                if api_key == API_KEY:
                    return func(*args, **kwargs)
                else:
                    app.logger.warning("API Key mismatch.")
        app.logger.warning("Unauthorized access attempt.")
        abort(401)
    return wrapper

@app.route('/')
def index():
    return 'Web App is up and running'

def get_data(sheet_name):
    try:
        app.logger.info(f"Received data request for sheet: {sheet_name}")
        
        sheet = get_google_sheet(sheet_name)
        if sheet is None:
            return jsonify({"error": "Failed to access Google Sheet"}), 500
        
        # Fetch all records from the sheet
        records = sheet.get_all_records()
        
        response = jsonify(records)
        app.logger.info(f"Response: {response.get_json()}")
        return response, 200
    except Exception as e:
        app.logger.error(f"Get data error: {e}")
        return jsonify({"error": "Failed to retrieve data"}), 500

@app.route('/get_data_tides', methods=['GET'])
@require_api_key
def get_data_tides():
    return get_data("tides_web_scraped")

@app.route('/get_data_artetv', methods=['GET'])
@require_api_key
def get_data_artetv():
    return get_data("tv_guide_arte")

@app.route('/get_data_raiuno', methods=['GET'])
@require_api_key
def get_data_raiuno():
    return get_data("tv_guide_raiuno")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
