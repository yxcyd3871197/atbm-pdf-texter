from flask import Flask, request, jsonify, send_file
from pdf_processor import PDFProcessor
import os
import io

app = Flask(__name__)

def verify_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != os.environ.get('API_KEY'):
        return False
    return True

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>PDF API</title>
            <style>
                body {
                    background-color: #121212;
                    color: white;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 20px;
                }
                h1 {
                    color: #ff4081;
                }
                p {
                    font-size: 18px;
                }
                a {
                    color: #90caf9;
                    text-decoration: none;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <h1>🚀 PDF API RUNNING!</h1>
            <p>Send POST Requests to /add-text with your PDF-file and Text-config.</p>
        </body>
    </html>
    """

@app.route('/add-text', methods=['POST'])
def add_text():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'Keine PDF-Datei gefunden'}), 400

        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return jsonify({'error': 'Keine Datei ausgewählt'}), 400

        text_config = request.form.get('config')
        if not text_config:
            return jsonify({'error': 'Keine Textkonfiguration gefunden'}), 400

        processor = PDFProcessor()
        result_pdf = processor.add_text_to_pdf(pdf_file, text_config)

        return send_file(
            result_pdf,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='result.pdf'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
