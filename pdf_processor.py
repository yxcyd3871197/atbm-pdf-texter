from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
import json
import os
import io

class PDFProcessor:
    def __init__(self):
        self.fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        self._register_fonts()

    def _register_fonts(self):
        if not os.path.exists(self.fonts_dir):
            os.makedirs(self.fonts_dir)

        for font_file in os.listdir(self.fonts_dir):
            if font_file.endswith(('.ttf', '.otf')):
                font_name = os.path.splitext(font_file)[0]
                font_path = os.path.join(self.fonts_dir, font_file)
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                except Exception as e:
                    print(f"Fehler beim Registrieren der Schriftart {font_name}: {str(e)}")

    def _convert_pixels_to_points(self, pixels):
        """Konvertiert Pixel (96 DPI) zu PDF-Punkten (72 DPI)"""
        return float(pixels) * 72 / 96

    def _draw_aligned_text(self, canvas, text, x, y, width, alignment='left'):
        """Zeichnet Text mit spezifischem Alignment"""
        try:
            if alignment == 'left':
                canvas.drawString(x, y, text)
            elif alignment == 'center':
                text_width = stringWidth(text, canvas._fontname, canvas._fontsize)
                center_x = x + (width/2) - (text_width/2)
                canvas.drawString(center_x, y, text)
            elif alignment == 'right':
                text_width = stringWidth(text, canvas._fontname, canvas._fontsize)
                right_x = x + width - text_width
                canvas.drawString(right_x, y, text)
            else:
                canvas.drawString(x, y, text)  # Fallback auf linksbündig
        except Exception as e:
            print(f"Fehler beim Text-Alignment: {str(e)}")
            canvas.drawString(x, y, text)  # Fallback auf linksbündig

    def _calculate_font_size(self, text, width, height, font_name, max_size=72, min_size=8):
        try:
            max_size_pt = self._convert_pixels_to_points(max_size)
            min_size_pt = self._convert_pixels_to_points(min_size)

            font_size = max_size_pt
            while font_size > min_size_pt:
                text_width = stringWidth(text, font_name, font_size)
                text_height = font_size

                if text_width <= width and text_height <= height:
                    return font_size

                font_size -= 1
            return min_size_pt
        except Exception as e:
            print(f"Fehler bei der Schriftgrößenberechnung: {str(e)}")
            return min_size_pt

    def add_text_to_pdf(self, pdf_file, text_config):
        try:
            config = json.loads(text_config)

            pdf_content = pdf_file.read()
            pdf_file_io = io.BytesIO(pdf_content)
            reader = PdfReader(pdf_file_io)
            writer = PdfWriter()

            if len(reader.pages) == 0:
                raise ValueError("Die PDF-Datei enthält keine Seiten")

            textfields = config.get('textfields', [])
            autofitfields = config.get('autofitfields', [])
            all_fields = textfields + autofitfields

            if not all_fields:
                raise ValueError('Keine Textfelder in der Konfiguration gefunden')

            max_page = max((field.get('page', 0) for field in all_fields), default=0)
            if max_page >= len(reader.pages):
                raise ValueError(f'Seite {max_page} existiert nicht in der PDF')

            for i in range(len(reader.pages)):
                page = reader.pages[i]

                page_textfields = [field for field in textfields if field.get('page', 0) == i]
                page_autofitfields = [field for field in autofitfields if field.get('page', 0) == i]

                if page_textfields or page_autofitfields:
                    packet = io.BytesIO()
                    c = canvas.Canvas(packet)

                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)
                    c.setPageSize((page_width, page_height))

                    # Normale Textfelder
                    for field in page_textfields:
                        try:
                            font = field.get('font', 'Helvetica')
                            size = self._convert_pixels_to_points(float(field.get('fontSize', 12)))
                            x = self._convert_pixels_to_points(float(field.get('x', 0)))
                            y = self._convert_pixels_to_points(float(field.get('y', 0)))
                            width = self._convert_pixels_to_points(float(field.get('width', 100)))
                            alignment = field.get('alignment', 'left')

                            c.setFont(font, size)

                            color = field.get('color', '#000000')
                            r = int(color[1:3], 16) / 255
                            g = int(color[3:5], 16) / 255
                            b = int(color[5:7], 16) / 255
                            c.setFillColor(Color(r, g, b))

                            self._draw_aligned_text(c, field.get('text', ''), x, y, width, alignment)
                        except Exception as e:
                            print(f"Fehler bei Textfeld: {str(e)}")
                            continue

                    # Autofit Textfelder
                    for field in page_autofitfields:
                        try:
                            font = field.get('font', 'Helvetica')
                            width = self._convert_pixels_to_points(float(field.get('width', 100)))
                            height = self._convert_pixels_to_points(float(field.get('height', 100)))
                            x = self._convert_pixels_to_points(float(field.get('x', 0)))
                            y = self._convert_pixels_to_points(float(field.get('y', 0)))
                            alignment = field.get('alignment', 'left')
                            max_size = float(field.get('maxFontSize', 72))
                            min_size = float(field.get('minFontSize', 8))

                            optimal_size = self._calculate_font_size(
                                field.get('text', ''),
                                width,
                                height,
                                font,
                                max_size,
                                min_size
                            )

                            c.setFont(font, optimal_size)

                            color = field.get('color', '#000000')
                            r = int(color[1:3], 16) / 255
                            g = int(color[3:5], 16) / 255
                            b = int(color[5:7], 16) / 255
                            c.setFillColor(Color(r, g, b))

                            self._draw_aligned_text(c, field.get('text', ''), x, y, width, alignment)
                        except Exception as e:
                            print(f"Fehler bei Autofit-Textfeld: {str(e)}")
                            continue

                    c.save()
                    packet.seek(0)

                    text_pdf = PdfReader(packet)
                    if text_pdf.pages:
                        page.merge_page(text_pdf.pages[0])

                writer.add_page(page)

            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            return output

        except Exception as e:
            raise ValueError(f"Fehler bei der PDF-Verarbeitung: {str(e)}")