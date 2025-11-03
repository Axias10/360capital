# 🧪 Test OCR Mistral - Guide d'utilisation

Ce guide explique comment tester la qualité de l'OCR Mistral avec vos images.

## 📋 Prérequis

```bash
pip install mistralai pillow
```

## 🔐 Configuration (Recommandé)

Pour plus de sécurité, utilisez des variables d'environnement:

```bash
# Créez un fichier .env (déjà dans .gitignore)
cp .env.example .env

# Éditez .env et ajoutez votre clé API
MISTRAL_API_KEY=votre_clé_ici
MISTRAL_SERVER_URL=https://api.05d3a00300de.dc.mistral.ai
```

Puis chargez les variables:

```bash
export $(cat .env | xargs)
```

## 🚀 Utilisation

### Script Simplifié (Recommandé)

Teste l'OCR sur n'importe quelle image sans dépendance Excel:

```bash
# Avec l'image par défaut du projet
python test_ocr_mistral_simple.py

# Avec votre propre image
python test_ocr_mistral_simple.py chemin/vers/votre/image.png
```

**Fonctionnalités:**
- ✅ Fonctionne sur Linux/macOS/Windows
- ✅ Sauvegarde automatique des résultats dans `ocr_results/`
- ✅ Statistiques de performance (durée, taille)
- ✅ Comptage de mots/lignes/caractères
- ✅ Support des variables d'environnement
- ✅ Gestion d'erreurs complète

### Script Excel (macOS uniquement)

Pour capturer et OCR des plages Excel:

```bash
python test_ocr_mistral_excel.py
```

**Note:** Nécessite macOS et Microsoft Excel installé.

## 📊 Résultats

Les résultats sont sauvegardés dans `ocr_results/`:

```
ocr_results/
├── ocr_360_capital_vc_logo_20231103_143022.txt      # Texte extrait
└── ocr_360_capital_vc_logo_20231103_143022.json     # Métadonnées complètes
```

Le fichier JSON contient:
- Texte extrait
- Durée du traitement
- Taille de l'image
- Timestamp
- Informations du modèle

## 🧪 Exemples de test

### Test 1: Logo (image simple)

```bash
python test_ocr_mistral_simple.py 360_capital_vc_logo.jpeg
```

### Test 2: Capture d'écran Excel

1. Faites une capture d'écran de votre tableau Excel
2. Sauvegardez-la comme `tableau_test.png`
3. Lancez:

```bash
python test_ocr_mistral_simple.py tableau_test.png
```

### Test 3: Comparer plusieurs images

```bash
# Testez plusieurs images et comparez les résultats
for img in *.png; do
    python test_ocr_mistral_simple.py "$img"
done
```

## 📈 Évaluer la qualité

Pour évaluer la qualité de l'OCR:

1. **Précision du texte:** Comparez le texte extrait avec l'original
2. **Vitesse:** Vérifiez la durée dans les métadonnées
3. **Formats supportés:** Testez différents types d'images (tableaux, texte simple, graphiques)
4. **Langues:** Testez avec du texte français/anglais/mixte

## 🔍 Dépannage

### Erreur: "mistralai n'est pas installé"

```bash
pip install mistralai
```

### Erreur: "MISTRAL_API_KEY non définie"

Vérifiez que vous avez exporté la variable:

```bash
echo $MISTRAL_API_KEY
```

Si vide, exportez-la:

```bash
export MISTRAL_API_KEY="votre_clé"
```

### Erreur: API connection failed

Vérifiez que le SERVER_URL est correct:

```bash
export MISTRAL_SERVER_URL="https://api.05d3a00300de.dc.mistral.ai"
```

## 💡 Conseils

- **Qualité d'image:** Utilisez des images nettes (300 DPI minimum)
- **Contraste:** Assurez-vous d'un bon contraste texte/fond
- **Taille:** Les images trop grandes peuvent prendre plus de temps
- **Format:** PNG et JPEG sont supportés

## 📝 Prochaines étapes

Pour améliorer votre workflow OCR:

1. **Automatisation:** Créez un script qui traite un dossier d'images
2. **Validation:** Ajoutez des tests de régression
3. **Comparaison:** Comparez avec d'autres solutions OCR (Tesseract, Azure, etc.)
4. **Post-traitement:** Ajoutez du nettoyage de texte automatique
