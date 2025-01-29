import unittest
from pdf_processor import PDFProcessor
import io
import json

class TestPDFProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_add_text_to_pdf(self):
        # Erstelle eine einfache PDF für Tests
        pdf_content = io.BytesIO()
        c = canvas.Canvas(pdf_content)
        c.drawString(100, 100, "Test PDF")
        c.save()
        pdf_content.seek(0)

        # Test-Konfiguration
        config = {
            "text": "Test Text",
            "page": 0,
            "x": 50,
            "y": 50,
            "font": "Helvetica",
            "fontSize": 12,
            "color": "#000000"
        }

        # Verarbeite PDF
        result = self.processor.add_text_to_pdf(
            io.BytesIO(pdf_content.read()),
            json.dumps(config)
        )

        # Überprüfe ob Ergebnis eine PDF ist
        self.assertIsInstance(result, io.BytesIO)

if __name__ == '__main__':
    unittest.main()