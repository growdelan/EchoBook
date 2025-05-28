# Translator eBooków EPUB

Aplikacja do tłumaczenia eBooków w formacie EPUB na język polski przy użyciu API OpenAI (model gpt-4.1-mini).

## Wymagania

- Python 3.11 lub nowszy
- Klucz API OpenAI

## Konfiguracja

Ustaw klucz API OpenAI jako zmienną środowiskową:

```bash
export OPENAI_API_KEY="twój-klucz-api"
```

Alternatywnie, możesz podać klucz API jako argument podczas uruchamiania aplikacji.

## Użycie

```bash
uv run main.py ścieżka/do/pliku.epub [opcje]
```

### Opcje

- `-o`, `--output-dir` - katalog wyjściowy dla przetłumaczonych plików (domyślnie: `output`)
- `-k`, `--api-key` - klucz API OpenAI (opcjonalnie, domyślnie używa zmiennej środowiskowej)

### Przykład

```bash
uv run main.py ksiazka.epub --output-dir przetlumaczone
```

## Struktura Projektu

- `main.py` - główny skrypt do tłumaczenia EPUB
- `translator/` - pakiet zawierający moduły aplikacji:
  - `api_client.py` - obsługa komunikacji z OpenAI API
  - `epub_processor.py` - wczytywanie, manipulacja i zapis EPUB
  - `text_splitter.py` - dzielenie tekstu na fragmenty odpowiednie dla API
- `output/` - katalog na przetłumaczone pliki EPUB

## Uwagi

- Aplikacja zachowuje oryginalne formatowanie i wszystkie elementy graficzne.
- Przetłumaczona wersja zostaje zapisana jako `<oryginalny_tytuł>-pl.epub` w katalogu wyjściowym.