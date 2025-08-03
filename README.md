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

- `-o`, `--output-dir`   katalog wyjściowy dla przetłumaczonych plików (domyślnie: `output`)
- `-k`, `--api-key`      klucz API OpenAI (opcjonalnie, domyślnie używa zmiennej środowiskowej)
- `-w`, `--workers`      liczba równoległych zapytań tłumaczących (domyślnie: `10`)

### Przykład

```bash
uv run main.py ksiazka.epub --output-dir przetlumaczone --workers 5
```

## Struktura Projektu

- `main.py`   – główny skrypt CLI (równoległe tłumaczenie fragmentów)
- `translator/` – pakiet z modułami aplikacji:
  - `api_client.py` – komunikacja z OpenAI API
  - `epub_processor.py` – wczytywanie, manipulacja i zapis EPUB
  - `text_splitter.py` – dzielenie HTML na fragmenty do tłumaczenia
- `output/` – katalog z przetłumaczonymi plikami EPUB

## Uwagi

- Aplikacja zachowuje oryginalne formatowanie i wszystkie elementy graficzne.
- Przetłumaczona wersja zostaje zapisana jako `<oryginalny_tytuł>-pl.epub` w katalogu wyjściowym.
- Od wersji **0.1.1** tłumaczenia wysyłane są równolegle (parametr `--workers`) z retry do 3 prób na fragment.
