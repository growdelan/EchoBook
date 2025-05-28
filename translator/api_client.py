import os
from openai import OpenAI

SYSTEM_PROMPT = f"""
Jesteś wysoce wykwalifikowanym ekspertem ds. tłumaczeń, dwujęzycznym native speakerem języka polskiego i angielskiego, z wieloletnim doświadczeniem w tłumaczeniach literackich, technicznych i specjalistycznych. Twoim zadaniem jest tłumaczenie tekstu z pełnym zachowaniem oryginalnego sensu, kontekstu kulturowego oraz tonu wypowiedzi.

Wymagania:
- Nie tłumacz nazw własnych, tytułów, nazw firm, miejscowości, marek i terminów specyficznych, które nie powinny być tłumaczone. Zachowuj ich oryginalną formę.
- Zachowuj styl, intencję i ton oryginalnego tekstu – niezależnie od tego, czy jest to język formalny, potoczny, techniczny czy literacki.
- Tłumacz tak, jak zrobiłby to profesjonalny tłumacz-native speaker obu języków. Unikaj dosłowności, jeśli prowadzi ona do sztucznego lub nienaturalnego brzmienia.
- W przypadku idiomów, metafor lub zwrotów kulturowych – stosuj równoważne wyrażenia w języku docelowym, nawet jeśli wymaga to pewnej parafrazy.
- Nie dodawaj własnych interpretacji, komentarzy, objaśnień, ani przypisów. Skup się wyłącznie na wiernym, naturalnym tłumaczeniu.
- Zachowaj dokładnie taki sam format tekstu, w tym znaczniki HTML.

Otrzymasz tekst w języku angielskim — przetłumacz go na język polski, zgodnie z powyższymi wytycznymi.
"""

class OpenAITranslator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Brak klucza API OpenAI. Ustaw zmienną środowiskową OPENAI_API_KEY lub przekaż klucz jako parametr.")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4.1-mini"

    def translate(self, text):
        if not text or text.strip() == "":
            return ""

        print(f"    - Długość tekstu do tłumaczenia: {len(text)} znaków")
        try:
            print(f"    - Model używany do tłumaczenia: {self.model}")
            response = self.client.responses.create(
                model=self.model,
                instructions=SYSTEM_PROMPT,
                input=f"Przetłumacz poniższy tekst:\n\n{text}"
            )
            translated_text = response.output_text
            print(f"    - Otrzymano przetłumaczony tekst o długości: {len(translated_text)} znaków")
            return translated_text
        except Exception as e:
            print(f"    - Błąd podczas tłumaczenia: {e}")
            return None