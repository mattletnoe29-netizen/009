TEST DE VISITE AVEC CONSENTEMENT

Contenu
- app.py : application Flask.
- requirements.txt : dépendance Python.

Collecte
- Date/heure UTC, famille du navigateur et type d'appareil approximatif.
- Enregistrement uniquement après clic sur « J'accepte le test ».
- L'application n'enregistre pas l'adresse IP, les mots de passe ou les comptes.
- Les résultats sont stockés dans visites.jsonl.

Lancement local
1. Installer Python.
2. `pip install -r requirements.txt`
3. `python app.py`
4. Ouvrir http://127.0.0.1:8080

Hébergement public
Ce ZIP ne crée pas automatiquement un lien Internet. Il faut déployer l'application sur un hébergeur compatible Python/Flask.
Configure obligatoirement les variables d'environnement ADMIN_USER et ADMIN_PASSWORD avec des valeurs fortes avant d'ouvrir /admin. La page des résultats refuse l'accès si aucun mot de passe n'est configuré.
L'hébergeur doit fournir HTTPS. Ne publie pas le journal JSONL ni les secrets.
Pour un service public, ajoute une notice de confidentialité adaptée et vérifie les règles applicables (notamment RGPD/ePrivacy en France).
