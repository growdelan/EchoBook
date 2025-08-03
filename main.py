#!/usr/bin/env python3
import os
import sys
import argparse
import time
from translator.api_client import OpenAITranslator
from translator.epub_processor import EPUBProcessor
from translator.text_splitter import TextSplitter


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

    return parser.parse_args()


def main():
    start_time = time.time()
    args = parse_arguments()

    print("[1/6] Sprawdzanie pliku wejściowego...")
    # Sprawdzenie czy plik wejściowy istnieje
    if not os.path.exists(args.input_file):
        print(f"Błąd: Plik '{args.input_file}' nie istnieje.")
        sys.exit(1)

    # Utworzenie katalogu wyjściowego, jeśli nie istnieje
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"Utworzono katalog wyjściowy: {args.output_dir}")

    print(f"[2/6] Wczytywanie pliku EPUB ({args.input_file})...")
    # Inicjalizacja procesora EPUB
    processor = EPUBProcessor(args.input_file)
    if not processor.load_epub():
        print("Błąd podczas wczytywania pliku EPUB.")
        sys.exit(1)

    print("[3/6] Ekstrakcja zawartości EPUB...")
    # Wczytanie zawartości EPUB
    if not processor.extract_content():
        print("Błąd podczas ekstrakcji zawartości z pliku EPUB.")
        sys.exit(1)
    print(f"Znaleziono {len(processor.content_items)} elementów do przetworzenia.")

    print("[4/6] Inicjalizacja tłumacza...")
    # Inicjalizacja tłumacza
    try:
        translator = OpenAITranslator(args.api_key)
    except ValueError as e:
        print(f"Błąd: {e}")
        sys.exit(1)

    # Inicjalizacja splittera tekstu
    text_splitter = TextSplitter()

    # Przetłumaczenie zawartości
    print("[5/6] Rozpoczęcie tłumaczenia zawartości...")
    translated_items = []
    total_items = len(processor.content_items)

    for index, item in enumerate(processor.content_items, 1):
        item_start_time = time.time()
        print(f"Tłumaczenie elementu {index}/{total_items}: {item['href']}...")

        html_data = text_splitter.split_html_for_translation(item["content"])
        elements_count = len(html_data["elements"]) if html_data["elements"] else 0

        if html_data["elements"]:
            print(
                f"  - Znaleziono {elements_count} elementów tekstowych do tłumaczenia"
            )

            # Pobranie tekstów do tłumaczenia
            texts_to_translate = [element["text"] for element in html_data["elements"]]

            # Łączymy wszystkie teksty w jeden dokument do tłumaczenia
            combined_text = "\n---SEPARATOR---\n".join(texts_to_translate)
            combined_length = len(combined_text)
            print(f"  - Przygotowano tekst o długości {combined_length} znaków")

            # Tłumaczenie całego dokumentu
            print("  - Wysyłanie zapytania do API tłumaczenia...")
            translation_start = time.time()
            translated_combined = translator.translate(combined_text)
            translation_time = time.time() - translation_start

            if translated_combined:
                print(f"  - Otrzymano odpowiedź z API (czas: {translation_time:.2f}s)")

                # Podział przetłumaczonego tekstu z powrotem na fragmenty
                translated_parts = translated_combined.split("\n---SEPARATOR---\n")

                # Aktualizacja HTML z przetłumaczonymi tekstami
                print(f"  - Aktualizacja HTML przetłumaczonymi tekstami...")
                translated_html = text_splitter.update_html_with_translations(
                    html_data, translated_parts[: len(html_data["elements"])]
                )

                translated_items.append(
                    {
                        "id": item["id"],
                        "href": item["href"],
                        "translated_html": translated_html,
                    }
                )
            else:
                print(f"  - Błąd: Pominięto tłumaczenie dla {item['href']} - błąd API.")
                translated_items.append(
                    {
                        "id": item["id"],
                        "href": item["href"],
                        "translated_html": item[
                            "content"
                        ],  # Zachowujemy oryginalny HTML
                    }
                )
        else:
            print("  - Brak tekstu do tłumaczenia, zachowanie oryginalnego HTML")
            # Brak tekstu do tłumaczenia, zachowujemy oryginalny HTML
            translated_items.append(
                {
                    "id": item["id"],
                    "href": item["href"],
                    "translated_html": item["content"],
                }
            )

        item_time = time.time() - item_start_time
        print(
            f"  - Zakończono przetwarzanie elementu {index}/{total_items} (czas: {item_time:.2f}s)"
        )
        print(f"  - Postęp: {index}/{total_items} ({(index / total_items * 100):.1f}%)")
        print("------------------------------------------------")

    # Aktualizacja zawartości EPUB przetłumaczonymi tekstami
    print("[6/6] Aktualizacja zawartości EPUB przetłumaczonymi tekstami...")
    update_start_time = time.time()
    processor.update_content_with_translation(translated_items)
    update_time = time.time() - update_start_time
    print(f"Zakończono aktualizację zawartości (czas: {update_time:.2f}s)")

    # Zapis przetłumaczonego EPUB
    output_filename = processor.generate_output_filename()
    output_path = os.path.join(args.output_dir, output_filename)

    print(f"Zapisywanie przetłumaczonego pliku EPUB: {output_path}...")
    save_start_time = time.time()
    if processor.save_translated_epub(output_path):
        save_time = time.time() - save_start_time
        total_time = time.time() - start_time

        print(f"Zapisano przetłumaczony plik EPUB (czas: {save_time:.2f}s)")
        print("============================")
        print(f"Tłumaczenie zakończone. Zapisano przetłumaczony plik: {output_path}")
        print(
            f"Całkowity czas wykonania: {total_time:.2f}s ({(total_time / 60):.2f} minut)"
        )
    else:
        print("Błąd podczas zapisywania przetłumaczonego pliku EPUB.")
        sys.exit(1)


if __name__ == "__main__":
    main()
