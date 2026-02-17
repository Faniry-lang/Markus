import json
import os
import re

class Provider:
    def generate_response_from_text(self, text: str) -> dict:
        raise NotImplementedError("generate_response_from_text doit être implémenté dans la sous-classe.")


def _extract_json_from_text(text: str) -> str:
    """
    Essaie d'extraire un fragment JSON valide depuis une chaîne de texte qui peut contenir
    du markdown (```json ... ```), du texte libre ou d'autres annotations.

    Retourne la sous-chaîne JSON brute si trouvée, sinon lève une ValueError.
    """
    if not isinstance(text, str):
        raise ValueError("Text must be a string to extract JSON")

    s = text.strip()
    fence_match = re.search(r"```(?:json)?\n(.*)\n```$", s, flags=re.DOTALL | re.IGNORECASE)
    if fence_match:
        candidate = fence_match.group(1).strip()
        return candidate
    idx_obj_start = s.find('{')
    idx_arr_start = s.find('[')

    if idx_obj_start != -1 and (idx_arr_start == -1 or idx_obj_start < idx_arr_start):
        idx_obj_end = s.rfind('}')
        if idx_obj_end != -1 and idx_obj_end > idx_obj_start:
            return s[idx_obj_start:idx_obj_end+1]

    if idx_arr_start != -1:
        idx_arr_end = s.rfind(']')
        if idx_arr_end != -1 and idx_arr_end > idx_arr_start:
            return s[idx_arr_start:idx_arr_end+1]

    try:
        json.loads(s)
        return s
    except Exception:
        raise ValueError("Aucun fragment JSON détectable dans le texte fourni")


class SimpleGoogleProvider(Provider):
    def __init__(self, api_key: str = None):
        try:
            import importlib
            genai = importlib.import_module('google.genai')
            types = getattr(genai, 'types', None) or importlib.import_module('google.genai').types
        except Exception as e:
            raise RuntimeError("Le SDK google-genai n'est pas installé. Installez 'google-genai' ou utilisez MockProvider pour le développement offline.")

        self.api_key = api_key or os.getenv("GOOGLE_GENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Aucune clé API trouvée. Définissez GOOGLE_GENAI_API_KEY dans les variables d'environnement.")

        self._genai = genai
        self._types = types
        self.client = self._genai.Client(api_key=self.api_key)

    def generate_response_from_text(self, text: str,
                                    model: str = "gemini-2.5-flash",
                                    temperature: float = 0,
                                    top_p: float = 0.95,
                                    top_k: int = 20) -> dict:

        response = self.client.models.generate_content(
            model=model,
            contents=self._types.Part.from_text(text=text),
            config=self._types.GenerateContentConfig(
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
            ),
        )

        if not hasattr(response, 'text') or not response.text:
            raise RuntimeError("Google provider returned empty response.text")

        raw = getattr(response, 'text')
        try:
            candidate = _extract_json_from_text(raw)
            parsed = json.loads(candidate)
        except Exception as e:
            raise RuntimeError(f"Impossible de parser la réponse Google en JSON: {e}\nRaw: {repr(raw)}")

        if not isinstance(parsed, dict):
            raise RuntimeError(f"Unexpected Google provider response type: {type(parsed).__name__}")

        return parsed

class OpenRouterProvider(Provider):

    def __init__(self, api_key:str = None):
        try:
            import importlib
            OpenAI = importlib.import_module('openai').OpenAI
        except Exception:
            raise RuntimeError("Package 'openai' requis pour OpenRouterProvider non installé.")

        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Aucune clé API trouvée. Définissez OPENROUTER_API_KEY dans les variables d'environnement.")
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.api_key)

    def generate_response_from_text(self, text: str, model:str = "nvidia/nemotron-nano-12b-v2-vl:free") -> dict:
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        if not hasattr(response, 'choices') or not response.choices:
            raise RuntimeError("OpenRouter returned no choices")
        if not hasattr(response.choices[0], 'message'):
            raise RuntimeError("OpenRouter choice has no message")
        if not hasattr(response.choices[0].message, 'content'):
            raise RuntimeError("OpenRouter message has no content")

        response_text = response.choices[0].message.content
        if not response_text:
            raise RuntimeError("OpenRouter returned empty content")

        raw = response_text
        try:
            candidate = _extract_json_from_text(raw)
            parsed_response = json.loads(candidate)
        except Exception as e:
            raise RuntimeError(f"Impossible de parser la réponse OpenRouter en JSON: {e}\nRaw: {repr(raw)}")

        if not isinstance(parsed_response, dict):
            raise RuntimeError(f"Unexpected OpenRouter provider response type: {type(parsed_response).__name__}")

        return parsed_response

class LocalProvider(OpenRouterProvider):
    def __init__(self):
        try:
            import importlib
            OpenAI = importlib.import_module('openai').OpenAI
        except Exception:
            raise RuntimeError("Package 'openai' requis pour OpenRouterProvider non installé.")
        super().__init__("")
        self.client = OpenAI(base_url="http://localhost:8080/v1", api_key="")
