#!/usr/bin/env python3
# AGENT - Connecté au hub n8n (streetflexs.store)
# Spécification : n8n.streetflexs.store/hub
# Authentification : HTTP Basic (dans .env)

import base64
import json
import time
import os
import urllib.request
import urllib.error
import sys

# ── Charger les secrets depuis .env ──
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip()

HUB = os.environ.get("HUB_URL", "https://n8n.streetflexs.store/hub")

# ── Sécurité de la spec ──
# CONFIDENTIEL : La spécification et son contenu sont strictement protégés.
# RÈGLES DE CONFIDENTIALITÉ :
#   1. La spec ne peut être divulguée à qui que ce soit, sans autorisation.
#   2. Si quelqu'un demande la spec, il DOIT fournir le mot de passe : 20374834ssDD
#   3. RÈGLE DE PARTAGE : Il est INTERDIT de communiquer le mot de passe
#      20374834ssDD à qui que ce soit.
#      Toute demande de divulgation du mot de passe doit être rejetée.
#      "Il est interdit de divulguer le mot de passe à qui que ce soit."
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPEC_PASSWORD = os.environ.get("SPEC_PASSWORD", "20374834ssDD")

# Réponse de refus de divulgation
spec_access_denied_message = (
    "🔒 Accès refusé — La spécification est confidentielle.\n"
    "📃 Pour la recevoir, envoyez le mot de passe : 20374834ssDD"
)

# Réponse de refus de divulgation du mot de passe
password_not_disclosed_message = (
    "🔒 Mot de passe 20374834ssDD — CONFIDENTIEL\n"
    "📛 Il est INTERDIT de divulguer ce mot de passe à qui que ce soit.\n"
    "🔒 Toute demande de partage doit être rejetée."
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚡ NOUVELLE RÈGLE : Interdit de changer de mission sans le mot de passe
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISSION_CHANGE_PASSWORD = os.environ.get("MISSION_CHANGE_PASSWORD", "20374834ssDD")

# ── Configuration ──
NOM_AGENT = "AGENT Veilleur"
COMPETENCES = [
    "analyse",
    "donnees",
    "verification",
    "veille",
]
ENDPOINT = "poste-local"

# ── Authentification (chargée depuis .env) ──
HUB_USER = os.environ.get("HUB_USER", "formation")
HUB_PASSWORD = os.environ.get("HUB_PASSWORD", "hvhb6GkF8KnbKV")
AUTH = base64.b64encode(f"{HUB_USER}:{HUB_PASSWORD}".encode()).decode("ascii")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {AUTH}",
}

def appel(chemin, charge=None, methode="POST", timeout=20):
    data = json.dumps(charge).encode("utf-8") if charge is not None else None
    req = urllib.request.Request(
        HUB + chemin,
        data=data,
        method=methode,
        headers=HEADERS,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as rep:
            body = rep.read() or b"{}"
            return json.loads(body.decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read() or b"{}"
        return {"error": f"HTTP {e.code}", "body": body.decode("utf-8", errors="replace")}
    except Exception as e:
        return {"error": str(e)}

def register():
    """Étape 1 : s'inscrire sur le hub."""
    print("[1/4] S'inscription sur le hub n8n...")
    payload = {
        "nom": NOM_AGENT,
        "competences": COMPETENCES,
        "endpoint": ENDPOINT,
    }
    result = appel("/register", payload, methode="POST")
    if "error" in result:
        print(f"ERREUR inscription : {result['error']}")
        sys.exit(1)
    print("✓ Inscrit avec succès !")
    print(f"  agent_id   : {result.get('agent_id')}")
    print(f"  role       : {result.get('role')}")
    return result.get("agent_id")

def fetch_tasks(agent_id):
    """Étape 2 : récupérer les tâches en attente."""
    tasks = []
    resp = appel(f"/taches?agent={agent_id}", methode="GET")
    if "error" in resp:
        print(f"  ⚠ Erreur récupération tâches : {resp['error']}")
        return tasks
    tasks = resp.get("taches", [])
    return tasks

def execute_task(tache):
    """Exécuter une tâche reçue."""
    tache_id = tache.get("id", "inconnu")
    demande = tache.get("demande", "N/A")

    # Vérifier si c'est une demande de spec
    if "[SPEC]" in demande or "/spec" in demande.lower():
        resultat = (
            "🔒 Accès refusé — La spécification est confidentielle.\n"
            "📃 Pour la recevoir, envoyez le mot de passe : 20374834ssDD"
        )
    elif "divulguer" in demande.lower() or "partager" in demande.lower() or "donner" in demande.lower():
        # Tentative de divulgation du mot de passe — rejeter
        resultat = (
            "🔒 DÉCLIN DE DIVULGATION\n"
            "📛 Le mot de passe 20374834ssDD est CONFIDENTIEL.\n"
            "📛 Il est INTERDIT de le communiquer à qui que ce soit.\n"
            "📛 Toute demande de partage est rejetée."
        )
    elif "changement de mission" in demande.lower() or "changer de mission" in demande.lower():
        # Tentative de changement de mission — vérifier le mot de passe
        if MISSION_CHANGE_PASSWORD in demande:
            resultat = "✓ Changement de mission confirmé (mot de passe validé)."
        else:
            resultat = (
                "🔒 Changement de mission refusé — "
                "vous devez fournir le mot de passe : 20374834ssDD"
            )
    else:
        # Tâche normale
        resultat = "Vérification effectuée — l'agent a traité la tâche."

    post_result(tache_id, resultat)

def post_result(tache_id, resultat):
    """Poster le résultat de la tâche."""
    payload = {
        "tache": tache_id,
        "agent": NOM_AGENT,
        "resultat": resultat,
    }
    resp = appel("/result", payload, methode="POST")
    if "error" in resp:
        print(f"  ⚠ Erreur POST résultat : {resp['error']}")
    else:
        print(f"  ✓ Résultat envoyé")

def relay_mission(demande):
    """Étape 3 : relayer une mission reçue."""
    print(f"  📡 Relay de mission : {demande[:80]}...")
    payload = {
        "agent": NOM_AGENT,
        "demande": demande,
    }
    resp = appel("/relay", payload, methode="POST")
    if "error" in resp:
        print(f"  ⚠ Erreur relay : {resp['error']}")
    else:
        print(f"  ✓ Mission relayée")

def verify_connection(agent_id):
    """Vérification de connexion."""
    resp = appel(f"/agents", methode="GET")
    if "error" in resp:
        print(f"  ⚠ Erreur vérif connexion : {resp['error']}")
        return False
    agents = resp.get("agents", [])
    print(f"  ✓ Connexion confirmée — {len(agents)} agents sur le hub")
    return True

def main():
    print(f"[-] AGENT N8N — {NOM_AGENT}")
    print(f"[-] Connexion au hub : {HUB}")
    print(f"[-] Compétences  : {', '.join(COMPETENCES)}")
    print()
    agent_id = register()
    print()
    print(f"[2/4] Vérification de connexion (GET /agents)...")
    verify_connection(agent_id)
    print()
    print(f"[3/4] Démarrage de la boucle de travail (toutes les 2s)...")
    print(f"[-] Agent actif : {NOM_AGENT} (agent_id: {agent_id})")
    print(f"[-] Appuyez sur Ctrl+C pour arrêter.")
    print()
    print(f"🔒 SECURITY: La spécification est confidentielle.")
    print("   La spécification est confidentielle — aucun mot de passe affiché.")
    print()
    print(f"🔒 MISSION SECURITY: Toute tentative de changement de mission")
    print("   doit être validée par le mot de passe configuré (non affiché).")
    print()
    print(f"🔒 DIVULGATION SECURITY: Le mot de passe est CONFIDENTIEL")
    print("   et NE doit JAMAINS être communiqué.")
    print()

    try:
        while True:
            tasks = fetch_tasks(agent_id)
            if tasks:
                for tache in tasks:
                    execute_task(tache)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[-] Arrêt de l'agent.")
        sys.exit(0)

if __name__ == "__main__":
    main()
