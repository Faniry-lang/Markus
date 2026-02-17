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

---

Journal de développement — JOUR 2
---
Date : 2026-02-17

Objectif du jour : ajouter l'exécution de scripts, la validation interactive des actions dangereuses, améliorer le parsing des réponses des providers, et suivre les étapes (step tracking) dans l'agent.

JOUR 2 — Checklist
- [x] Ajouter l'exécution de commandes/scripts (outil `execute_command`).
- [x] Ajouter une validation interactive avant d'exécuter des actions sensibles (outil `validator`).
- [x] Ajouter un décorateur pour marquer les fonctions exposées à Markus et indiquer si elles nécessitent une validation (`markus_function`).
- [x] Améliorer le parsing des réponses JSON renvoyées par les providers (extraction d'un fragment JSON dans du texte brut ou bloqué en markdown).
- [x] Supporter un provider local/alternatif (`LocalProvider`) et intégrer OpenRouter/Google providers.
- [x] Ajouter un suivi d'étapes (current_step / next_step) dans `MarkusAgent` pour faciliter l'orchestration.

Fichiers modifiés (résumé)
- `core/functions/script.py`
  - Ajout de `execute_command(command: str, args: list[str])` qui exécute une commande via `subprocess.run` et retourne stdout.
  - L'outil est décoré avec `@markus_function(needs_validation=True)` pour forcer une confirmation utilisateur avant exécution.

- `core/utils/validator.py` (nouveau)
  - Fournit `get_validation_from_console_input(tool_name, tool_args)` : prompt console interactif demandant O/N à l'utilisateur pour autoriser l'exécution.
  - Arbitre l'exécution des outils marqués `needs_validation`.

- `core/decorator/function_decorator.py`
  - Ajout du décorateur `markus_function(needs_validation: bool = False)` qui marque les fonctions comme appelables par l'agent et attache l'attribut `_needs_validation`.

- `core/agent.py`
  - Ajout / renforcement de la structure `MarkusResponse` (champs : action, tool_name, tool_args, response_text, current_step, next_step, error_message).
  - Boucle d'orchestration : lecture des `current_step`/`next_step`, accumulation d'un `context` à réinjecter dans le prompt, appel des outils via `call_tool()`.
  - Logging des réponses finales dans `markus.log`.
  - Note importante : le code actuel concatène dans `context` les résultats d'appels d'outils (ex: `Résultat de list_dir: {...}`), mais il conserve uniquement ces sorties textuelles et pas explicitement le dernier message de l'IA. Voir la section "Remarques" ci‑dessous.

- `core/providers.py`
  - Ajout d'une fonction d'extraction `_extract_json_from_text(text)` qui tente d'isoler un fragment JSON dans une réponse brute (supporte fences markdown ```json ... ``` et objets/arrays bruts).
  - Les providers (`SimpleGoogleProvider`, `OpenRouterProvider`) utilisent l'extraction et lèvent maintenant des erreurs claires lorsque le parsing JSON échoue (avec le raw response en message d'erreur).
  - `LocalProvider` étend le comportement pour pointer vers une instance locale (utile pour développement offline).

- `core/main.py`
  - CLI : création d'un agent via `_create_agent()` et boucle interactive `shell()` (typer). Par défaut, l'agent instancié dans l'exemple utilise `OpenRouterProvider`.

- `test.py`
  - Fichier de test d'exécution simple (ex: print / exécution manuelle pour valider `execute_command`).

Décisions et notes
- Constat observé : le provider peut renvoyer du texte non JSON (ou encadré par des backticks). Le code tente d'extraire un fragment JSON mais plusieurs erreurs d'analyse apparaissent (ex: "Impossible de parser la réponse Google en JSON" avec le raw print). Ces erreurs sont maintenant remontées proprement et enregistrées.
- Suggestion d'amélioration (faible risque, recommandé) :
  - Au lieu de stocker uniquement les "derniers appels d'outils" dans `context`, ajouter un champ dédié pour stocker le "dernier message de l'IA" ou l'historique succinct des messages IA (par ex. `last_ai_message` ou `conversation_history` avec les 3-5 derniers éléments). Cela permettrait au provider (et au prompt) de mieux comprendre l'intention et d'éviter les boucles où l'IA répète des outputs d'outil sans ajouter de directives claires.
  - Bénéfices : contexte plus explicite pour le LLM, meilleure continuité de la conversation, facilite le débogage des séquences où l'IA renvoie des appels d'outil répétés.
  - Impact minimal sur l'API : ajouter un champ `last_ai_message` (string) au `context` géré par `MarkusAgent.run()` et l'inclure dans le prompt envoyé au provider.

Couverture des objectifs
- Exécution de script: Done
- Validation interactive: Done
- Décorateur / annotation des fonctions: Done
- Parsing robuste des providers: Done (mais peut être encore amélioré si des providers renvoient formats inattendus)
- Local provider: Done
- Suivi d'étapes: Done

Fin du journal — JOUR 2
