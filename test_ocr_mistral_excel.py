# test_ocr_mistral_excel.py

import os
import subprocess
import base64
from PIL import Image
from mistralai import Mistral

# ================= CONFIGURATION =================
MISTRAL_API_KEY = "X7DpYENEsRkosAnYZJbd6exXoUDhETWy"  # Ta clé OCR
SERVER_URL = "https://api.05d3a00300de.dc.mistral.ai"

EXCEL_FILE = "/Users/justinkim/Documents/GitHub/360capital/audrey_extract/digitaly_one-pager_-_version_justin.xlsx"        # Remplace par ton fichier
CELL_RANGE = "K17:V68"                   # Plage à capturer
OUTPUT_IMAGE = "capture_tableau.png"     # Image temporaire
# ================================================

def capture_excel_to_image(excel_file, cell_range, output_image):
    """Capture une plage Excel via AppleScript (macOS)"""
    excel_file = os.path.abspath(excel_file)
    output_image = os.path.abspath(output_image)

    applescript = f'''
    tell application "Microsoft Excel"
        activate
        open "{excel_file}"
        delay 2
        tell active sheet of active workbook
            select range "{cell_range}"
            copy range "{cell_range}"
        end tell
        delay 1
        close active workbook saving no
    end tell
    quit application "Microsoft Excel"
    '''

    print("Capture de la plage Excel...")
    subprocess.run(['osascript', '-e', applescript], timeout=30)

    # Sauvegarde du presse-papier comme image
    save_script = f'''
    set theFile to POSIX file "{output_image}"
    try
        set imageData to (the clipboard as «class PNGf»)
        set fileRef to open for access theFile with write permission
        write imageData to fileRef
        close access fileRef
        return "OK"
    on error
        return "ERREUR"
    end try
    '''

    result = subprocess.run(['osascript', '-e', save_script], capture_output=True, text=True)
    if os.path.exists(output_image):
        img = Image.open(output_image)
        print(f"Image capturée : {output_image} ({img.width}x{img.height})")
        return output_image
    else:
        print("Échec : image non générée")
        print(result.stdout)
        return None

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def ocr_with_mistral(image_path):
    client = Mistral(server_url=SERVER_URL, api_key=MISTRAL_API_KEY)

    print("\nEnvoi à Mistral OCR (mistral-ocr-latest)...")
    base64_image = encode_image(image_path)

    try:
        response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:image/png;base64,{base64_image}"
            },
            include_image_base64=False  # On veut juste le texte
        )
        print("OCR terminé !\n")
        return response.text
    except Exception as e:
        print(f"Erreur OCR : {e}")
        return None

# ====================== TEST ======================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST OCR MISTRAL SUR CAPTURE EXCEL")
    print("=" * 60)

    # Étape 1 : Capture
    image_path = capture_excel_to_image(EXCEL_FILE, CELL_RANGE, OUTPUT_IMAGE)
    if not image_path:
        print("Arrêt : impossible de capturer l'image")
        exit()

    # Étape 2 : OCR
    ocr_text = ocr_with_mistral(image_path)

    if ocr_text:
        print("=" * 60)
        print("RÉSULTAT OCR (Mistral) :")
        print("=" * 60)
        print(ocr_text)
        print("=" * 60)
    else:
        print("Échec de l'OCR")

    # Nettoyage optionnel
    # os.remove(image_path)
