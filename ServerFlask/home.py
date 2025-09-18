from flask import Flask, request, send_from_directory, render_template_string
import os
from datetime import datetime
import subprocess

app = Flask(__name__)
BASE_DIR = os.path.join("timestamps", "download")

# Assicurati che la cartella base esista
os.makedirs(BASE_DIR, exist_ok=True)


# Route principale che mostra la lista delle cartelle con i file marcati temporalmente
@app.route("/", methods=["GET"])
def index():
    # Crea una pagina HTML con la lista delle cartelle disponibili
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

# Route che permette di scaricare i file di una cartella
@app.route("/download/<folder>") 
def download_folder(folder):
    path = os.path.join(BASE_DIR, folder)
    files = os.listdir(path)
    html = f"<h2>File in {folder}</h2><ul>"
    for f in files:
        html += f'<li><a href="/file/{folder}/{f}">{f}</a></li>'
    html += "</ul><a href='/'>Torna indietro</a>"
    return html

@app.route("/file/<folder>/<filename>")
def serve_file(folder, filename):
    directory = os.path.join(BASE_DIR, folder)
    return send_from_directory(directory, filename,as_attachment=True)


# Route che permette di inviare i dati da marcare temporalmente
@app.route("/timestamp", methods=["POST"]) 
def timestamp_data():
    # Il server legge i dati dal corpo della richiesta
    data = request.get_data(as_text=True).strip()

    if not data:
        return "Errore: dati vuoti", 400
    
    # Si crea una nuova cartella basata su data e ora
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_path = os.path.join(BASE_DIR, timestamp)
    os.makedirs(folder_path)
    txt_path = os.path.join(folder_path, "dati_" + timestamp + ".txt")

    # Si scrive i dati nel file .txt
    with open(txt_path, "w") as f:
        f.write(data)

    try:
        # Si esegue la marcatura temporale con 2 calendar funzionanti
        subprocess.run([
            "ots", "stamp",
            "--calendar", "https://a.pool.opentimestamps.org",
            "--calendar", "https://b.pool.opentimestamps.org",
            txt_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        os.remove(txt_path)  # Rimuove il file .txt se la marca temporale fallisce
        os.rmdir(folder_path)  # Rimuove la cartella se la marca temporale fallisce
        return f"Errore durante la marca temporale: {e}", 500
    # Dopo ciò, se l'operazione va a buon fine 
    # il comando ots stamp creerà un file .ots nella stessa cartella del file .txt
    
    return f"Marca temporale creata con successo in {folder_path}", 200
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
