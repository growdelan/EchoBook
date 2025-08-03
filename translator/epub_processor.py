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
            print(f"  – Wczytywanie pliku EPUB: {self.input_path}")
            self.book = epub.read_epub(self.input_path)
            print("  – Plik EPUB wczytany pomyślnie")
            return True
        except Exception as e:
            print(f"Błąd podczas wczytywania pliku EPUB: {e}")
            return False

    def extract_content(self):
        self.content_items = []
        if not self.book:
            print("  – Błąd: Brak wczytanego pliku EPUB")
            return False
        print("  – Rozpoczęcie ekstrakcji zawartości EPUB…")
        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content().decode("utf-8")
                self.content_items.append(
                    {
                        "id": item.id,
                        "href": item.get_name(),
                        "content": content,
                        "item": item,
                    }
                )
        print(f"  – Wyodrębniono {len(self.content_items)} dokumentów")
        return True

    def update_content_with_translation(self, translated_items):
        for translated in translated_items:
            for original in self.content_items:
                if original["id"] == translated["id"]:
                    original["item"].set_content(translated["translated_html"].encode("utf-8"))
                    break

    def save_translated_epub(self, output_path):
        try:
            epub.write_epub(output_path, self.book, {})
            return True
        except Exception as e:
            print(f"Błąd podczas zapisywania pliku EPUB: {e}")
            return False

    def generate_output_filename(self):
        base = os.path.basename(self.input_path)
        name, ext = os.path.splitext(base)
        return f"{name}-pl{ext}"
