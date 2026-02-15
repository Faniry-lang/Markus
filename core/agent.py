import json
import logging
from typing import Any, Dict
from pydantic import BaseModel
from core.utils.tools import get_markus_tools, tools_registry
from core.providers import Provider

logging.basicConfig(
    filename="markus.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

class MarkusResponse(BaseModel):

    action: str
    tool_name: str | None = None
    tool_args: Dict[str, Any] | None = None
    response_text: str | None = None
    current_step: str | None = None
    next_step: str | None = None
    error_message: str | None = None


def call_tool(tool_name: str, tool_args: Dict[str, Any]) -> Any:
    tool_func = tools_registry.get(tool_name)
    if not tool_func:
        raise ValueError(f"Outil '{tool_name}' non trouvé.")
    return tool_func(**tool_args)

class MarkusAgent:
    def __init__(self, provider: Provider):
        self.provider = provider
        tools_description = get_markus_tools()
        self.system_prompt = f"""
        Tu es Markus, un assistant IA destiné à aider l'utilisateur avec des tâches sur son ordinateur.
        Tu peux appeler les outils suivants:
        {tools_description}

        Quand tu réponds, tu DOIS renvoyer un JSON avec la structure exacte suivante:
        {{
            "action": "tool_call" | "text" | "error",
            "tool_name": "nom_de_l_outil" | null,
            "tool_args": {{ "arg1": valeur1, ... }} | null,
            "response_text" : "reponse finale, à remplir uniquement quand la demande de l'utilisateur aura été satisfaite ou si une erreur est survenue" | null,
            "current_step": "description de ce que tu fais (ex: d'abord appeler la fonction do_something())",
            "next_step" : "description ce que tu vas faire après avoir eu le résultat (ex: ensuite je vais appeler la fonction then()" | null,
            "error_message": "message si action=error" | null
        }}

        Ne renvoie **jamais** autre chose que ce JSON et ne mets pas de backtricks comme ceci à la réponse: "```json", nous avons \n
        juste besoin du JSON.
        
        La requête de l'utilisateur peut ne pas être satisfaite en un seul appel, tu es encouragé à diviser
        ta tâche en étape, selon les outils et leurs arguments, si tu n'es pas capable de satisfaire la
        demande, il faut le dire à l'utilisateur. Utilise les contextes précédents pour te situer, s'ils existent 
        """

    def generate(self, prompt: str) -> MarkusResponse:
        try:
            response = self.provider.generate_response_from_text(
                text=self.system_prompt + "\nUser: " + prompt
            )

            if response is None:
                raise ValueError("Le provider a retourné None.")
            if not isinstance(response, dict):
                raise ValueError(f"Provider returned non-mapping response: {type(response).__name__}")
            if "action" not in response:
                raise ValueError("Provider response missing 'action' field.")

            return MarkusResponse(**response)
        except Exception as e:
            logging.exception("Erreur lors de la génération de la réponse du provider")
            return MarkusResponse(action="error", error_message=str(e))

    def run(self, user_text: str) -> str:
        context = ""
        max_iterations = 12
        attempts = 0
        current_step: str | None = None
        while True:
            attempts += 1
            if attempts > max_iterations:
                return (
                    "Markus a atteint le nombre maximal d'itérations sans produire de réponse finale. "
                    "Il semble qu'il y ait une boucle. Interrompu pour éviter une boucle infinie."
                )

            prompt = f"{user_text}\nContexte précédent: {context}"
            response = self.generate(prompt)

            if response.action == "text" and response.response_text:
                logging.info(json.dumps({
                    "user_input": user_text,
                    "agent_response": response.response_text
                }, ensure_ascii=False))
                return response.response_text

            elif response.action == "tool_call":
                if response.current_step:
                    current_step = response.current_step
                    context += f"\nEtape actuelle: {current_step}"
                if response.next_step:
                    next_step = response.next_step
                    context += f"\nProchaine étape: {next_step}"

                if not response.tool_name:
                    context += "\nRéponse de provider: appel d'outil sans nom d'outil."
                    return "Erreur: appel d'outil sans nom fourni par le provider."

                try:
                    tool_result = call_tool(response.tool_name, response.tool_args or {})
                    context += f"\nRésultat de {response.tool_name}: {tool_result}"
                except Exception as e:
                    context += f"\nErreur lors de l'appel de {response.tool_name}: {e}"
                    context += "\nMarkus doit réessayer ou signaler l'erreur."

            elif response.action == "error":
                return f"Erreur rencontrée par Markus: {response.error_message}"
