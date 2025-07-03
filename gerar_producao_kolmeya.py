import pandas as pd

# Exemplo: lista de envios Kolmeya
envios = [
    {"telefone": "11999999999", "data_envio": "2024-06-01"},
    {"telefone": "11888888888", "data_envio": "2024-06-02"},
    # ... outros envios ...
]

# Exemplo: lista de vendas IPLUC
vendas_ipluc = [
    {"telefone": "11999999999", "data_venda": "2024-06-02"},
    # ... outras vendas ...
]

# Transformar em DataFrame
df_envios = pd.DataFrame(envios)
df_vendas = pd.DataFrame(vendas_ipluc)

# Cruzar pelo telefone
df_merged = pd.merge(df_envios, df_vendas, on="telefone", how="inner")

# Adicionar colunas extras
df_merged["status_venda"] = "vendido"
df_merged["canal"] = "KOLMEYA"

# Salvar CSV
df_merged.to_csv("producao_kolmeya.csv", index=False)
print("Arquivo producao_kolmeya.csv gerado com sucesso!")