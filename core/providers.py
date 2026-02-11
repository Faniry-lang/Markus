import os
from google import genai
from google.genai import types

class Provider:
    def generate_response_from_text(self, text: str) -> str:
        raise NotImplementedError("generate_response_from_text doit être implémenté dans la sous-classe.")


class SimpleGoogleProvider(Provider):
    def __init__(self, api_key: str = None):

        self.api_key = api_key or os.getenv("GOOGLE_GENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Aucune clé API trouvée. Définissez GOOGLE_GENAI_API_KEY dans les variables d'environnement.")

        self.client = genai.Client(api_key=self.api_key)

    def generate_response_from_text(self, text: str,
                                    model: str = "gemini-2.5-flash",
                                    temperature: float = 0,
                                    top_p: float = 0.95,
                                    top_k: int = 20) -> str:

        response = self.client.models.generate_content(
            model=model,
            contents=types.Part.from_text(text=text),
            config=types.GenerateContentConfig(
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
            ),
        )
        return response.text


