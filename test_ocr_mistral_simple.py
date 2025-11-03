#!/usr/bin/env python3
"""
Script simplifié pour tester la qualité de l'OCR Mistral
Sans dépendance Excel - fonctionne avec n'importe quelle image
"""

import os
import sys
import base64
import json
from datetime import datetime
from pathlib import Path

try:
    from mistralai import Mistral
except ImportError:
    print("❌ Erreur: mistralai n'est pas installé")
    print("Installez avec: pip install mistralai")
    sys.exit(1)

# ================= CONFIGURATION =================
# Utilisez des variables d'environnement pour plus de sécurité:
# export MISTRAL_API_KEY="votre_clé"
# export MISTRAL_SERVER_URL="https://api.05d3a00300de.dc.mistral.ai"

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "X7DpYENEsRkosAnYZJbd6exXoUDhETWy")
SERVER_URL = os.getenv("MISTRAL_SERVER_URL", "https://api.05d3a00300de.dc.mistral.ai")

# Image par défaut dans le projet
DEFAULT_IMAGE = "360_capital_vc_logo.jpeg"
OUTPUT_DIR = "ocr_results"
# ================================================


def encode_image(image_path):
    """Encode une image en base64"""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"❌ Erreur: Image non trouvée: {image_path}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de l'encodage: {e}")
        return None


def ocr_with_mistral(image_path, save_results=True):
    """
    Effectue l'OCR avec Mistral et retourne le résultat

    Args:
        image_path: Chemin vers l'image
        save_results: Si True, sauvegarde les résultats dans un fichier

    Returns:
        dict avec 'success', 'text', 'metadata'
    """
    print(f"\n📸 Image: {image_path}")

    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": f"Image non trouvée: {image_path}",
            "text": None
        }

    # Infos sur l'image
    file_size = os.path.getsize(image_path) / 1024  # KB
    print(f"📊 Taille: {file_size:.2f} KB")

    # Client Mistral
    client = Mistral(server_url=SERVER_URL, api_key=MISTRAL_API_KEY)

    print(f"🚀 Envoi à Mistral OCR (mistral-ocr-latest)...")
    print(f"🔗 Serveur: {SERVER_URL}")

    base64_image = encode_image(image_path)
    if not base64_image:
        return {
            "success": False,
            "error": "Échec de l'encodage de l'image",
            "text": None
        }

    start_time = datetime.now()

    try:
        response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:image/png;base64,{base64_image}"
            },
            include_image_base64=False
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"✅ OCR terminé en {duration:.2f}s\n")

        result = {
            "success": True,
            "text": response.text if hasattr(response, 'text') else str(response),
            "metadata": {
                "image_path": image_path,
                "file_size_kb": file_size,
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat(),
                "model": "mistral-ocr-latest",
                "server_url": SERVER_URL
            }
        }

        if save_results:
            save_ocr_result(result)

        return result

    except Exception as e:
        print(f"❌ Erreur OCR: {e}")
        return {
            "success": False,
            "error": str(e),
            "text": None,
            "metadata": {
                "image_path": image_path,
                "timestamp": datetime.now().isoformat()
            }
        }


def save_ocr_result(result):
    """Sauvegarde le résultat OCR dans un fichier"""
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    # Nom du fichier basé sur l'image et timestamp
    image_name = Path(result["metadata"]["image_path"]).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Sauvegarde du texte
    txt_file = f"{OUTPUT_DIR}/ocr_{image_name}_{timestamp}.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(result["text"])
    print(f"💾 Texte sauvegardé: {txt_file}")

    # Sauvegarde des métadonnées en JSON
    json_file = f"{OUTPUT_DIR}/ocr_{image_name}_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"💾 Métadonnées sauvegardées: {json_file}")


def print_result(result):
    """Affiche le résultat de manière formatée"""
    print("=" * 70)
    print("📄 RÉSULTAT OCR MISTRAL")
    print("=" * 70)

    if result["success"]:
        print(f"\n✅ Succès!")
        if "metadata" in result:
            meta = result["metadata"]
            print(f"⏱️  Durée: {meta.get('duration_seconds', 'N/A')}s")
            print(f"📏 Taille image: {meta.get('file_size_kb', 'N/A'):.2f} KB")

        print(f"\n{'─' * 70}")
        print("📝 TEXTE EXTRAIT:")
        print(f"{'─' * 70}\n")
        print(result["text"])
        print(f"\n{'─' * 70}")

        # Stats basiques
        if result["text"]:
            words = len(result["text"].split())
            lines = len(result["text"].split('\n'))
            chars = len(result["text"])
            print(f"\n📊 Statistiques:")
            print(f"   • Caractères: {chars}")
            print(f"   • Mots: {words}")
            print(f"   • Lignes: {lines}")
    else:
        print(f"\n❌ Échec: {result.get('error', 'Erreur inconnue')}")

    print("=" * 70)


def main():
    """Fonction principale"""
    print("=" * 70)
    print("🧪 TEST OCR MISTRAL - VERSION SIMPLIFIÉE")
    print("=" * 70)

    # Vérifier la clé API
    if not MISTRAL_API_KEY or MISTRAL_API_KEY == "":
        print("❌ MISTRAL_API_KEY non définie!")
        print("Définissez-la avec: export MISTRAL_API_KEY='votre_clé'")
        sys.exit(1)

    # Déterminer l'image à utiliser
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = DEFAULT_IMAGE
        print(f"\nℹ️  Utilisation de l'image par défaut: {DEFAULT_IMAGE}")
        print(f"   Pour tester une autre image: python {sys.argv[0]} chemin/vers/image.png\n")

    # Exécuter l'OCR
    result = ocr_with_mistral(image_path, save_results=True)

    # Afficher le résultat
    print_result(result)

    # Code de sortie
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
