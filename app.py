from flask import Flask, request, render_template_string, Response
from datetime import datetime, timezone
import json
import os
import hmac

app = Flask(__name__)
LOG_FILE = os.environ.get("LOG_FILE", "visites.jsonl")
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

PAGE = """
<!doctype html><html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Test de visite</title>
<style>
body{font-family:system-ui,sans-serif;max-width:680px;margin:36px auto;padding:0 16px;line-height:1.55;color:#17202a}
main{border:1px solid #d5d8dc;border-radius:14px;padding:22px}
button{padding:12px 16px;border:0;border-radius:8px;background:#2457c5;color:white;font-weight:700}
.small{color:#566573;font-size:.94rem}
</style></head><body><main>
<h1>Test de statistiques de visite</h1>
<p>Cette page sert à tester un petit système de statistiques.</p>
<p>Si tu acceptes, le propriétaire du test enregistrera :</p>
<ul><li>la date et l'heure UTC ;</li><li>la famille de navigateur ;</li><li>le type d'appareil approximatif.</li></ul>
<p><strong>L'adresse IP n'est pas enregistrée par cette application.</strong>
Aucun mot de passe, message ou compte personnel n'est collecté.</p>
<form method="post" action="/consent"><button type="submit">J'accepte le test</button></form>
<p class="small">Aucune donnée n'est enregistrée par l'application si tu ne cliques pas sur le bouton. Ne participe que si tu comprends et acceptes ce test.</p>
</main></body></html>
"""
THANKS = """<!doctype html><html lang="fr"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Merci</title>
<body style="font-family:system-ui;max-width:680px;margin:36px auto;padding:0 16px">
<h1>Merci !</h1><p>Ton accord a été enregistré avec les données techniques indiquées.</p></body></html>"""

def classify_browser(ua):
    ua = (ua or "").lower()
    if "edg/" in ua: return "Edge"
    if "firefox/" in ua: return "Firefox"
    if "opr/" in ua or "opera" in ua: return "Opera"
    if "chrome/" in ua and "chromium" not in ua: return "Chrome"
    if "safari/" in ua and "chrome/" not in ua: return "Safari"
    return "Inconnu"

def classify_device(ua):
    ua = (ua or "").lower()
    if any(x in ua for x in ("android", "iphone", "ipad", "mobile")):
        return "Mobile/tablette (approx.)"
    if any(x in ua for x in ("windows", "macintosh", "linux")):
        return "Ordinateur (approx.)"
    return "Inconnu"

def admin_authorized():
    # On refuse l'accès si aucun mot de passe n'a été configuré.
    if not ADMIN_PASSWORD:
        return False
    auth = request.authorization
    return bool(auth and hmac.compare_digest(auth.username or "", ADMIN_USER)
                and hmac.compare_digest(auth.password or "", ADMIN_PASSWORD))

@app.get("/")
def home():
    return render_template_string(PAGE)

@app.post("/consent")
def consent():
    ua = request.headers.get("User-Agent", "")
    row = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "consent": True,
        "browser": classify_browser(ua),
        "device_approx": classify_device(ua)
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\\n")
    except OSError:
        return "Impossible d'enregistrer le résultat.", 500
    return render_template_string(THANKS)

@app.get("/admin")
def admin():
    if not admin_authorized():
        return Response("Accès réservé. Configure ADMIN_USER et ADMIN_PASSWORD.", 401,
                        {"WWW-Authenticate": 'Basic realm="Résultats du test"'})
    rows = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    html = """<!doctype html><html lang='fr'><meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>Résultats</title><body style='font-family:system-ui;margin:24px'>
    <h1>Résultats des tests consentis</h1><p>Nombre de consentements : {{ rows|length }}</p>
    <pre>{{ rows|tojson(indent=2) }}</pre></body></html>"""
    return render_template_string(html, rows=rows)

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host=host, port=port, debug=False)
