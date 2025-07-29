from flask import Flask, request, send_from_directory, render_template_string
import os
from datetime import datetime
import subprocess

app = Flask(__name__)
BASE_DIR = os.path.join("timestamps", "download")

os.makedirs(BASE_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    # Crea una lista delle cartelle disponibili
    folders = sorted(os.listdir(BASE_DIR), reverse=True)
    html = """
    <h1>Archivio Timestamp</h1>
    <ul>
    {% for folder in folders %}
      <li><a href="/download/{{folder}}">{{ folder }}</a></li>
    {% endfor %}
    </ul>
    """
    return render_template_string(html, folders=folders)

@app.route("/download/<folder>")
# Route per il download dei file
def download_folder(folder):
    path = os.path.join(BASE_DIR, folder)
    files = os.listdir(path)
    html = f"<h2>File in {folder}</h2><ul>"
    for f in files:
        html += f'<li><a href="/file/{folder}/{f}">{f}</a></li>'
    html += "</ul><a href='/'>Torna indietro</a>"
    return html

@app.route("/file/<folder>/<filename>")
# Download dei file
def serve_file(folder, filename):
    directory = os.path.join(BASE_DIR, folder)
    return send_from_directory(directory, filename,as_attachment=True)

@app.route("/timestamp", methods=["POST"])
def timestamp_data():
    # Legge i dati dal corpo della richiesta
    data = request.get_data(as_text=True).strip()


    if not data:
        return "Errore: dati vuoti", 400

    # Crea una nuova cartella basata su data e ora
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_path = os.path.join(BASE_DIR, timestamp)
    os.makedirs(folder_path)

    txt_path = os.path.join(folder_path, "dati_" + timestamp + ".txt")
    ots_path = txt_path + ".ots"

    # Scrive i dati nel file .txt
    with open(txt_path, "w") as f:
        f.write(data)

    try:
        # Marcatura temporale con 2 calendar funzionanti
        subprocess.run([
            "ots", "stamp",
            "--calendar", "https://a.pool.opentimestamps.org",
            "--calendar", "https://b.pool.opentimestamps.org",
            txt_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        return f"Errore durante la marca temporale: {e}", 500

    return f"Marca temporale creata con successo in {folder_path}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
