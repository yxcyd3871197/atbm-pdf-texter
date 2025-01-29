"""
# PDF Text API

Eine API zum Hinzufügen von Text zu PDF-Dateien.

## Installation

1. Erstelle einen 'fonts' Ordner
2. Lege deine .ttf oder .otf Schriftarten im 'fonts' Ordner ab
3. Installiere die Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
   ```

## API Verwendung

POST Request an `/add-text` mit:
- PDF Datei als 'pdf'
- JSON Konfiguration als 'config':

```json
{
    "text": "Dein Text",
    "page": 0,
    "x": 100,
    "y": 100,
    "font": "DeineSchriftart",
    "fontSize": 12,
    "color": "#000000"
}
```

## Beispiel-Anfrage mit curl:
```bash
curl -X POST -F "pdf=@input.pdf" -F 'config={"text":"Test","page":0,"x":100,"y":100,"font":"Arial","fontSize":12,"color":"#000000"}' http://localhost:8080/add-text -o output.pdf
```
"""