import requests
import csv
from datetime import datetime
import uuid

CLICKS_CSV_PATH = 'cliques_kolmeya.csv'

def get_investimento_kolmeya(token, start_at, end_at, limit=30000):
    url = "https://kolmeya.com.br/api/v1/sms/reports/statuses"
    headers = {
        "Authorization": f"Bearer 4YyZFPMQHW0LZeKiGAqe705cLPweuJKIWFtKAyuj",
        "Content-Type": "application/json"
    }
    body = {
        "start_at": start_at,
        "end_at": end_at,
        "limit": limit
    }
    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        print("Status code:", response.status_code)
        print("Resposta bruta:", response.text)
        response.raise_for_status()
        try:
            data = response.json()
        except Exception as e:
            print("Erro ao decodificar JSON:", e)
            return {"erro": "Erro na resposta da API"}
        return data
    except requests.exceptions.Timeout:
        print("Timeout na requisição à API Kolmeya.")
        return {"erro": "Timeout na requisição à API Kolmeya."}
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão com a API Kolmeya: {e}")
        return {"erro": f"Erro de conexão com a API Kolmeya: {e}"}

def registrar_clique(user_id, campanha, ip, destino):
    """Registra um clique no arquivo CSV com uma chave única."""
    chave = str(uuid.uuid4()) 
    with open(CLICKS_CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([chave, datetime.now(), user_id, campanha, ip, destino])
    print(f"Chave gerada para clique: {chave}")  
    return chave

def ler_cliques():
    """Lê os cliques registrados e retorna como lista de dicionários."""
    cliques = []
    try:
        with open(CLICKS_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 6:
                    cliques.append({
                        "chave": row[0],
                        "data_hora": row[1],
                        "user_id": row[2],
                        "campanha": row[3],
                        "ip": row[4],
                        "destino": row[5]
                    })
    except FileNotFoundError:
        pass
    return cliques

if __name__ == "__main__":
    # Exemplo de chamada para testar
    registrar_clique("123", "kolmeya", "127.0.0.1", "https://wa.me/SEUNUMERO")
