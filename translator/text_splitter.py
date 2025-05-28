from bs4 import BeautifulSoup


class TextSplitter:
    def __init__(self, max_length=None):
        self.max_length = max_length
        
    def split_html_for_translation(self, html_content):
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Znajdujemy wszystkie elementy tekstowe do tłumaczenia
        text_elements = []
        self._extract_text_elements(soup, text_elements)
        
        return {
            'soup': soup,
            'elements': text_elements
        }
    
    def _extract_text_elements(self, node, text_elements):
        # Pomijamy skrypty, style i komentarze
        if node.name in ['script', 'style']:
            return
            
        # Sprawdzanie węzłów tekstowych
        if hasattr(node, 'contents'):
            for child in node.contents:
                if child.name:
                    self._extract_text_elements(child, text_elements)
                elif str(child).strip():
                    text_elements.append({
                        'node': child,
                        'text': str(child).strip()
                    })
    
    def update_html_with_translations(self, split_data, translations):
        for i, translation in enumerate(translations):
            if i < len(split_data['elements']):
                # Zamieniamy oryginalny tekst na tłumaczenie
                split_data['elements'][i]['node'].replace_with(translation)
        
        # Zwracamy zaktualizowany HTML
        return str(split_data['soup'])