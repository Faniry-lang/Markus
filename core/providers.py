import json
import os

class Provider:
    def generate_response_from_text(self, text: str) -> dict:
        raise NotImplementedError("generate_response_from_text doit être implémenté dans la sous-classe.")


class SimpleGoogleProvider(Provider):
    def __init__(self, api_key: str = None):
        try:
            from google import genai
            from google.genai import types
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

        try:
            parsed = json.loads(response.text)
        except Exception as e:
            raise RuntimeError(f"Impossible de parser la réponse Google en JSON: {e}\nRaw: {getattr(response, 'text', repr(response))}")

        if not isinstance(parsed, dict):
            raise RuntimeError(f"Unexpected Google provider response type: {type(parsed).__name__}")

        return parsed

class OpenRouterProvider(Provider):

    def __init__(self, api_key:str = None):
        try:
            from openai import OpenAI
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

        try:
            parsed_response = json.loads(response_text)
        except Exception as e:
            raise RuntimeError(f"Impossible de parser la réponse OpenRouter en JSON: {e}\nRaw: {response_text}")

        if not isinstance(parsed_response, dict):
            raise RuntimeError(f"Unexpected OpenRouter provider response type: {type(parsed_response).__name__}")

        return parsed_response

