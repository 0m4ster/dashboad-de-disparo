import os
import shutil
import time

download_dir = r'C:\Users\Junin\Downloads'  # Pasta onde o arquivo é baixado
destino = r'C:\Users\Junin\Desktop\dash\clientes'  # Pasta para onde mover
filename_fragment = 'leads'  # Parte do nome do arquivo
timeout = 60  # Tempo máximo de espera (segundos)

os.makedirs(destino, exist_ok=True)  # Garante que a pasta de destino existe

start_time = time.time()
downloaded = False

while time.time() - start_time < timeout:
    files = os.listdir(download_dir)
    for f in files:
        if filename_fragment in f and f.endswith('.csv'):
            caminho_origem = os.path.join(download_dir, f)
            caminho_destino = os.path.join(destino, f)
            shutil.move(caminho_origem, caminho_destino)
            downloaded = True
            print(f"Arquivo movido para {caminho_destino} com sucesso!")
            break
    if downloaded:
        break
    time.sleep(1)

if not downloaded:
    print("Arquivo não foi encontrado ou não foi baixado dentro do tempo esperado.")
