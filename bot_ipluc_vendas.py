import os
import argparse
import sys
import requests
import pandas as pd
from datetime import date

def obter_datas():
    parser = argparse.ArgumentParser(description="Consulta vendas IPLUC")
    parser.add_argument('--data_inicio', type=str, help='Data de início (YYYY-MM-DD)')
    parser.add_argument('--data_fim', type=str, help='Data de fim (YYYY-MM-DD)')
    args = parser.parse_args()

    if args.data_inicio and args.data_fim:
        return args.data_inicio, args.data_fim

    # Só pede input se rodar interativamente
    if sys.stdin.isatty():
        data_inicio = input("Data de início (YYYY-MM-DD, Enter para mês atual): ").strip()
        data_fim = input("Data de fim (YYYY-MM-DD, Enter para hoje): ").strip()
        if data_inicio and data_fim:
            return data_inicio, data_fim

    # Se não informou nada, usa padrão (mês atual)
    data_inicio = date.today().replace(day=1).isoformat()
    data_fim = date.today().isoformat()
    return data_inicio, data_fim

# === CONFIGURAÇÕES ===
# URL do endpoint da API de vendas do IPLUC
API_URL = "https://api.ipluc.com/vendas"  # Substitua pelo endpoint real

# Autenticação (exemplo com Bearer Token)
API_TOKEN = os.environ.get("IPLUC_API_TOKEN", "SEU_TOKEN_AQUI")  # Prefira variável de ambiente

print(f"DEBUG: Token lido = '{API_TOKEN}'")

if not API_TOKEN or API_TOKEN == "SEU_TOKEN_AQUI":
    print("Atenção: Defina a variável de ambiente IPLUC_API_TOKEN para maior segurança.")

# Parâmetros de consulta (datas flexíveis)
data_inicio, data_fim = obter_datas()

params = {
    "data_inicio": data_inicio,
    "data_fim": data_fim
}

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# === REQUISIÇÃO À API ===
try:
    response = requests.get(API_URL, headers=headers, params=params)
    response.raise_for_status()
    vendas = response.json()  # Ajuste conforme o formato retornado pela API

    if not isinstance(vendas, list):
        raise ValueError("Resposta inesperada da API: esperado uma lista de vendas.")

    df_vendas = pd.DataFrame(vendas)

    # Salva em CSV
    df_vendas.to_csv("vendas_ipluc.csv", index=False)
    print("Arquivo vendas_ipluc.csv gerado com sucesso!")

except Exception as e:
    print(f"Erro ao consultar a API do IPLUC: {e}")