import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


class EPUBProcessor:
    def __init__(self, input_path):
        self.input_path = input_path
        self.book = None
        self.content_items = []

    def load_epub(self):
        try:
            print(f"  - Wczytywanie pliku EPUB: {self.input_path}")
            self.book = epub.read_epub(self.input_path)
            print("  - Plik EPUB wczytany pomyślnie")
            return True
        except Exception as e:
            print(f"Błąd podczas wczytywania pliku EPUB: {e}")
            return False

    def extract_content(self):
        self.content_items = []

        if not self.book:
            print("  - Błąd: Brak wczytanego pliku EPUB")
            return False

        print("  - Rozpoczęcie ekstrakcji zawartości EPUB...")
        item_count = 0
        document_count = 0

        for item in self.book.get_items():
            item_count += 1
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                document_count += 1
                content = item.get_content().decode("utf-8")
                self.content_items.append(
                    {
                        "id": item.id,
                        "href": item.get_name(),
                        "content": content,
                        "item": item,
                    }
                )
                print(f"  - Wyodrębniono dokument: {item.get_name()}")

        print(
            f"  - Zakończono ekstrakcję zawartości: znaleziono {document_count} dokumentów z {item_count} elementów"
        )
        return True

    def get_text_for_translation(self):
        text_items = []

        for item in self.content_items:
            soup = BeautifulSoup(item["content"], "lxml")
            text = soup.get_text()
            if text.strip():
                text_items.append(
                    {
                        "id": item["id"],
                        "href": item["href"],
                        "text": text,
                        "original_html": item["content"],
                    }
                )

        return text_items

    def update_content_with_translation(self, translated_items):
        print(
            "  - Rozpoczęcie aktualizacji zawartości EPUB przetłumaczonymi tekstami..."
        )
        updated_count = 0

        for translated_item in translated_items:
            for item in self.content_items:
                if item["id"] == translated_item["id"]:
                    item["content"] = translated_item["translated_html"]
                    item["item"].set_content(
                        translated_item["translated_html"].encode("utf-8")
                    )
                    updated_count += 1
                    print(f"  - Zaktualizowano zawartość: {translated_item['href']}")
                    break

        print(
            f"  - Zakończono aktualizację zawartości: zaktualizowano {updated_count} z {len(translated_items)} elementów"
        )

    def save_translated_epub(self, output_path):
        try:
            print(f"  - Zapisywanie przetłumaczonego pliku EPUB: {output_path}")
            epub.write_epub(output_path, self.book, {})
            print("  - Plik EPUB zapisany pomyślnie")
            return True
        except Exception as e:
            print(f"Błąd podczas zapisywania przetłumaczonego pliku EPUB: {e}")
            return False

    def generate_output_filename(self):
        base_name = os.path.basename(self.input_path)
        name_without_ext, ext = os.path.splitext(base_name)
        return f"{name_without_ext}-pl{ext}"
