#!/usr/bin/env python3
"""CLI do tłumaczenia EPUB z równoległymi zapytaniami API.

Najmniejszy możliwy patch wprowadzający:
- parametr --workers / -w,
- równoległe tłumaczenie fragmentów ThreadPoolExecutor,
- retry z limitem 3 prób na fragment,
- zachowanie kolejności elementów w pliku wynikowym,
zgodnie z PRD 2025-08-03.
"""
import os
import sys
import argparse
import time
import concurrent.futures
from typing import Dict, Any, List

from translator.api_client import OpenAITranslator
from translator.epub_processor import EPUBProcessor
from translator.text_splitter import TextSplitter

MAX_RETRIES = 3  # z PRD


def parse_arguments():
    parser = argparse.ArgumentParser(description="Tłumacz eBooków EPUB na język polski")
    parser.add_argument("input_file", help="Ścieżka do pliku EPUB do przetłumaczenia")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="output",
        help="Katalog wyjściowy dla przetłumaczonych plików",
    )
    parser.add_argument(
        "-k",
        "--api-key",
        help="Klucz API OpenAI (opcjonalnie, domyślnie używa zmiennej środowiskowej OPENAI_API_KEY)",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=10,
        help="Liczba równoległych zapytań tłumaczących (domyślnie: 10)",
    )

    return parser.parse_args()


def translate_with_retry(translator: OpenAITranslator, text: str, max_attempts: int = MAX_RETRIES) -> str | None:
    """Tłumaczy tekst z retry. Zwraca None po niepowodzeniu."""
    for attempt in range(1, max_attempts + 1):
        translated = translator.translate(text)
        if translated:
            return translated
        if attempt < max_attempts:
            print(f"      – Retry {attempt}/{max_attempts}…")
    return None


def build_translated_item(
    index: int,
    item: Dict[str, Any],
    translator: OpenAITranslator,
    text_splitter: TextSplitter,
    total_items: int,
) -> Dict[str, Any]:
    item_start = time.time()
    print(f"Tłumaczenie elementu {index + 1}/{total_items}: {item['href']}…")

    html_data = text_splitter.split_html_for_translation(item["content"])
    elements = html_data["elements"] or []

    if not elements:
        print("  – Brak tekstu do tłumaczenia, zachowanie oryginalnego HTML")
        return {
            "id": item["id"],
            "href": item["href"],
            "translated_html": item["content"],
        }

    texts_to_translate = [el["text"] for el in elements]
    combined_text = "\n---SEPARATOR---\n".join(texts_to_translate)
    print(f"  – Łączna długość tekstu: {len(combined_text)} zn")

    translated_combined = translate_with_retry(translator, combined_text)
    if translated_combined is None:
        print("  – Pominięto (3 nieudane próby)")
        return {
            "id": item["id"],
            "href": item["href"],
            "translated_html": item["content"],
        }

    translated_parts = translated_combined.split("\n---SEPARATOR---\n")
    translated_html = text_splitter.update_html_with_translations(html_data, translated_parts[: len(elements)])

    item_time = time.time() - item_start
    print(f"  – Zakończono element {index + 1}/{total_items} (czas: {item_time:.2f}s)")
    return {
        "id": item["id"],
        "href": item["href"],
        "translated_html": translated_html,
    }


def main():
    start_time = time.time()
    args = parse_arguments()

    print("[1/6] Sprawdzanie pliku wejściowego…")
    if not os.path.exists(args.input_file):
        print(f"Błąd: Plik '{args.input_file}' nie istnieje.")
        sys.exit(1)
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"[2/6] Wczytywanie EPUB ({args.input_file})…")
    processor = EPUBProcessor(args.input_file)
    if not processor.load_epub() or not processor.extract_content():
        sys.exit(1)
    total_items = len(processor.content_items)
    print(f"Znaleziono {total_items} elementów do przetłumaczenia.")

    print("[3/6] Inicjalizacja klienta i narzędzi…")
    try:
        translator = OpenAITranslator(args.api_key)
    except ValueError as e:
        print(f"Błąd: {e}")
        sys.exit(1)
    text_splitter = TextSplitter()

    print("[4/6] Rozpoczęcie równoległego tłumaczenia…")
    translated_items: List[dict] = [None] * total_items
    completed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(build_translated_item, idx, item, translator, text_splitter, total_items): idx
            for idx, item in enumerate(processor.content_items)
        }

        for future in concurrent.futures.as_completed(futures):
            idx = futures[future]
            try:
                translated_items[idx] = future.result()
            except Exception as exc:
                print(f"  – Element {idx + 1} niezakończony z powodu: {exc}")
                item = processor.content_items[idx]
                translated_items[idx] = {
                    "id": item["id"],
                    "href": item["href"],
                    "translated_html": item["content"],
                }
            completed += 1
            print(f"Postęp: {completed}/{total_items} ({completed / total_items * 100:.1f}%)")

    print("[5/6] Aktualizacja EPUB przetłumaczonymi treściami…")
    processor.update_content_with_translation(translated_items)
    output_filename = processor.generate_output_filename()
    output_path = os.path.join(args.output_dir, output_filename)

    print("[6/6] Zapis pliku wynikowego…")
    if processor.save_translated_epub(output_path):
        total_time = time.time() - start_time
        print("============================")
        print(f"Tłumaczenie ukończone: {output_path}")
        print(f"Całkowity czas: {total_time:.2f}s ({total_time / 60:.2f} min)")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
