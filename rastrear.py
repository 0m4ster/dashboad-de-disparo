from flask import Flask, request, redirect
import csv
from datetime import datetime
import uuid

app = Flask(__name__)

CLICKS_CSV_PATH = 'cliques_kolmeya.csv'

@app.route('/')
def home():
    return "API Flask online! Use /rastrear para rastrear cliques."

@app.route('/rastrear')
def rastrear():
    chave = request.args.get('chave') or str(uuid.uuid4())
    user_id = request.args.get('user_id', 'desconhecido')
    campanha = request.args.get('campanha', 'desconhecida')
    destino = request.args.get('destino', 'https://wa.me/SEUNUMERO')
    ip = request.remote_addr

    # Salva o clique com a chave recebida ou gerada
    with open(CLICKS_CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([chave, datetime.now(), user_id, campanha, ip, destino])

    # Exibe no terminal para teste
    print(f"Clique registrado: chave={chave}, user_id={user_id}, campanha={campanha}, ip={ip}, destino={destino}")

    return redirect(destino)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 