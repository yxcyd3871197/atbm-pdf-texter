from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF
import json
import os
import io

class PDFProcessor:
    def __init__(self):
        self.fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')

    def add_text_to_pdf(self, pdf_file, text_config):
        config = json.loads(text_config)

        # PDF einlesen
        pdf_content = pdf_file.read()
        pdf_file_io = io.BytesIO(pdf_content)
        reader = PdfReader(pdf_file_io)
        writer = PdfWriter()

        page_num = config.get('page', 0)
        if page_num >= len(reader.pages):
            raise ValueError(f'Seite {page_num} existiert nicht in der PDF')

        for i in range(len(reader.pages)):
            page = reader.pages[i]

            if i == page_num:
                # Erstelle neue PDF für Text
                pdf = FPDF()
                pdf.set_auto_page_break(auto=False)
                pdf.add_page()

                # Setze Schriftart und Größe
                pdf.set_font('Helvetica', size=int(config.get('fontSize', 12)))

                # Konvertiere Hex-Farbe in RGB
                color = config.get('color', '#000000').lstrip('#')
                r = int(color[:2], 16)
                g = int(color[2:4], 16)
                b = int(color[4:], 16)
                pdf.set_text_color(r, g, b)

                # Füge Text hinzu
                pdf.text(
                    float(config.get('x', 0)),
                    float(config.get('y', 0)),
                    config.get('text', '')
                )

                # Speichere temporäre PDF
                temp_pdf = io.BytesIO()
                pdf.output(temp_pdf)
                temp_pdf.seek(0)

                # Füge Text-Layer zur original Seite hinzu
                text_pdf = PdfReader(temp_pdf)
                page.merge_page(text_pdf.pages[0])

            writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return output