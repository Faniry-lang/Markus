# Markus — Assistant IA local (Agent personnel)

Projet : Assistant IA local (agent personnel)

But
---
Fournir un assistant IA hébergé localement sur ton laptop, basé sur un LLM open‑source ou un provider Cloud pendant le développement, capable de comprendre des commandes en langage naturel et d'agir sur le système (ouvrir des applications, gérer des fichiers, lancer des commandes, naviguer sur le web).

Principes importants
- Fonctionne principalement hors‑ligne quand possible (mode local), mais le MVP utilise d'abord un provider cloud simple (SimpleGoogleProvider) pour la recherche web.
- Permissions strictes : toute action potentiellement dangereuse doit demander confirmation en mode interactif.
- Extensible : architecture plugin pour ajouter des providers, des outils et des interfaces (overlay GUI, API mobile).
- Traçabilité : journalisation (logs) de toutes les actions exécutées par l'agent.

Résumé du MVP
---
Livrables prioritaires (MVP jour 1):
- `MarkusAgent` fonctionnel avec `SimpleGoogleProvider` (recherche web).
- Outils de base pour :
  - manipulation de fichiers (créer / lire / supprimer / déplacer),
  - exécution de scripts (récupération stdout/stderr),
  - recherche web via le provider.
- Interface CLI agréable et utilisable (belle sortie, historique).

Structure du dépôt (extraits)
---
- `core/agent.py` — logique de l'agent et orchestration.
- `core/providers.py` — provider(s) de LLM / API (ex: `SimpleGoogleProvider`).
- `core/functions/` — outils exposés à l'agent (fs, exec, etc.).
- `core/utils/tools.py` — enregistrement et découverte des outils.
- `core/shell.py` — interface CLI interactive.
- `core/main.py` — point d'entrée pour tests/démonstration.

Journal de développement — JOUR 1
---
Objectif du jour : Construire `MarkusAgent` avec un `SimpleGoogleProvider` et fournir un MVP minimal permettant la manipulation de fichiers, l'exécution de scripts et la recherche web, accessible via une CLI "belle".

JOUR 1 — Checklist
- [ ] Instancier `MarkusAgent` avec `SimpleGoogleProvider` (lecture de la variable d'environnement `GOOGLE_GENAI_API_KEY` ou fallback `MockProvider`).
- [ ] Implémenter / vérifier les fonctions outils de fichier : `create_file`, `read_file`, `delete_file`, `move_file`.
- [ ] Implémenter `run_script` (exécuter un script Python/bash, récupérer stdout/stderr, limiter par timeout).
- [ ] Enregistrer ces fonctions dans le registre d'outils (`tools_registry`).
- [ ] Rendre la CLI (`core/shell.py`) agréable : couleurs, prompts clairs, historique (librairie recommandée : `rich` ou `prompt_toolkit`).
- [ ] Ajouter journalisation de base (logs/actions) dans `logs/`.
- [ ] Documenter le processus et fournir des tests manuels rapides (smoke tests).


Sécurité et permissions
---
- Par défaut, l'agent doit demander confirmation explicite pour :
  - exécution de scripts (surtout si elles touchent l'OS),
  - suppression de fichiers non restreints.
- Prévoir une option `--yes` (non sécurisée) pour exécution non interactive lors d'automatisations.
- Limiter l'exécution de scripts au dossier `workspace/sandbox/` par défaut (configurable).
- Ne jamais exfiltrer des fichiers locaux vers un provider cloud sans consentement explicite.

Risques connus et mitigations
- Exécution de code arbitraire : exiger confirmation et sandbox.
- Exposition de la clé API : recommandation d'utiliser variable d'environnement et ne pas l'écrire dans les logs.
- Dépendances cloud non disponibles : prévoir `MockProvider`.

Roadmap rapide (prochaines étapes)
1. Journées 2–3 : tests, robustesse et parsing LLM.
2. Journée 4 : sécurité renforcée, sandboxing, whitelist/blacklist.
3. Journées 5–7 : CLI avancée, providers locaux (offline), interface overlay et API mobile.


