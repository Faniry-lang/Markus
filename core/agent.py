import json
from typing import Any, Dict
from pydantic import BaseModel
from core.utils.tools import get_markus_tools, tools_registry
from core.providers import Provider

class MarkusResponse(BaseModel):

    action: str
    tool_name: str | None = None
    tool_args: Dict[str, Any] | None = None
    response_text: str | None = None
    error_message: str | None = None


def call_tool(tool_name: str, tool_args: Dict[str, Any]) -> Any:
    tool_func = tools_registry.get(tool_name)
    if not tool_func:
        raise ValueError(f"Outil '{tool_name}' non trouvé.")
    return tool_func(**tool_args)

import re
import json

def parse_llm_json(response_text: str):
    cleaned = re.sub(r"^```json\s*|\s*```$", "", response_text.strip(), flags=re.MULTILINE)
    json_match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    else:
        return {"action": "text", "response_text": response_text}

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
            "response_text": "texte si action=text" | null,
            "error_message": "message si action=error" | null
        }}

        Ne renvoie **jamais** autre chose que ce JSON.
        """

    def generate(self, prompt: str) -> MarkusResponse:
        try:
            raw_response = self.provider.generate_response_from_text(
                text=self.system_prompt + "\nUser: " + prompt
            )
            data = parse_llm_json(raw_response)
            return MarkusResponse(**data)
        except json.JSONDecodeError:
            return MarkusResponse(action="text", response_text=raw_response)
        except Exception as e:
            return MarkusResponse(action="error", error_message=str(e))

    def run(self, user_text: str) -> str:
        context = ""
        while True:
            prompt = f"{user_text}\nContexte précédent: {context}"
            response = self.generate(prompt)

            if response.action == "text":
                return response.response_text

            elif response.action == "tool_call":
                try:
                    tool_result = call_tool(response.tool_name, response.tool_args or {})
                    context += f"\nRésultat de {response.tool_name}: {tool_result}"
                except Exception as e:
                    context += f"\nErreur lors de l'appel de {response.tool_name}: {e}"
                    context += "\nMarkus doit réessayer ou signaler l'erreur."

            elif response.action == "error":
                return f"Erreur rencontrée par Markus: {response.error_message}"

