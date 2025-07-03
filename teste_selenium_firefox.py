from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.common.exceptions import TimeoutException
import os
import shutil

driver_path = r'C:\Users\Junin\Desktop\dash\geckodriver.exe'  # ajuste se necessário

# Crie o objeto Service
service = Service(executable_path=driver_path)

# Inicia o Firefox usando o Service
driver = webdriver.Firefox(service=service)

# Acesse diretamente a tela de login
driver.get('https://crm.ipluc.com/users/login')

time.sleep(2)

# Aguarde até estar na URL correta (menos restritivo)
wait = WebDriverWait(driver, 20)
wait.until(EC.url_contains("users/login"))

# Aguarde até o campo de usuário estar presente (usando placeholder exato)
email_input = wait.until(EC.presence_of_element_located((By.ID, "login")))
email_input.send_keys("pepmaciel@servcredrp.com.br")

senha_input = wait.until(EC.presence_of_element_located((By.ID, "senha")))
senha_input.send_keys("Pep050609")

entrar_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Entrar')]")))
entrar_button.click()

# Aguarde o login ser processado
time.sleep(5)

def fluxo_leads(driver, wait):
    # Aguarde o desaparecimento do loading antes de clicar em Leads
    wait.until(EC.invisibility_of_element_located((By.ID, "loadingdefault")))
    # Aguarde o botão 'Leads' estar clicável e clique nele
    leads_btn = wait.until(EC.element_to_be_clickable((By.ID, "menu-4")))
    leads_btn.click()

    # Aguarde o desaparecimento do loading antes de clicar no botão 'Filtro'
    wait.until(EC.invisibility_of_element_located((By.ID, "loadingdefault")))

    # Clique no botão 'Filtro'
    filtro_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Filtro']/parent::button")))
    filtro_btn.click()

    # Clique no seletor de status (segundo dropdown)
    status_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[contains(@class, 'vscomp-value')])[2]")))
    status_dropdown.click()
    time.sleep(1)

    # Buscar o campo de pesquisa que está visível (não oculto)
    search_inputs = driver.find_elements(By.XPATH, "//input[contains(@class, 'vscomp-search-input')]")
    for search_input in search_inputs:
        if search_input.is_displayed():
            driver.execute_script("arguments[0].focus();", search_input)
            driver.execute_script("arguments[0].value = 'vendido'; arguments[0].dispatchEvent(new Event('input'));", search_input)
            break
    time.sleep(1)

    # Listar os textos das opções após digitar
    options = driver.find_elements(By.XPATH, "//div[contains(@class, 'vscomp-option')]//span")
    for opt in options:
        print(f"Texto encontrado: '{opt.text}'")

    # Buscar por 'Cliente Vendido - H' com contains, rolar até a opção antes de clicar
    option = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'vscomp-option')]//span[contains(text(), 'Cliente Vendido - H')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", option)
    time.sleep(0.2)
    option.click()

    # Clicar no campo de texto superior para fechar o dropdown
    defocus = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Nome, cpf ou telefone do lead']")))
    defocus.click()

    # Clicar no botão 'Aplicar Filtro' pelo id
    aplicar_btn = wait.until(EC.element_to_be_clickable((By.ID, "btn-aplicar-filtros")))
    aplicar_btn.click()

    # Aguarde o desaparecimento do loading antes de clicar no botão do usuário
    wait.until(EC.invisibility_of_element_located((By.ID, "loadingdefault")))

    # Clicar no botão do usuário/header dropdown
    user_dropdown_btn = wait.until(EC.element_to_be_clickable((By.ID, "page-header-user-dropdown")))
    user_dropdown_btn.click()

    # Clicar no botão 'Exportar' do menu do usuário
    exportar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Exportar']")))
    exportar_btn.click()

    # Aguarda o botão azul 'Exportar' da modal e clica nele
    modal_exportar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'modal')]//button[normalize-space()='Exportar']")))
    modal_exportar_btn.click()

    # Aguarda a modal sumir (até 20 segundos)
    try:
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "modal")))
    except TimeoutException:
        print("Modal já estava fechada ou não encontrada, seguindo o fluxo.")

    # Tenta clicar no X se ele aparecer, mas se não conseguir, clica no body para fechar a modal
    try:
        fechar_modal_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-close') and @aria-label='Close']"))
        )
        driver.execute_script("arguments[0].click();", fechar_modal_btn)
        print("Botão X clicado com sucesso!")
    except TimeoutException:
        print("Botão X não encontrado ou não clicável, tentando clicar fora da modal.")
        body = driver.find_element(By.TAG_NAME, "body")
        body.click()
        time.sleep(1)

def fluxo_exporta_baixa_move(driver, wait):
    try:
        try:
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "modal")))
        except TimeoutException:
            print("Modal já estava fechada ou não encontrada, seguindo o fluxo.")
        time.sleep(2)
        relatorio_btn = wait.until(EC.element_to_be_clickable((By.ID, "menu-52")))
        relatorio_btn.click()
        exportacoes_csv_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Exportações CSV']")))
        exportacoes_csv_btn.click()
        tabela_baixar = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'Baixar')]")))
        wait.until(EC.invisibility_of_element_located((By.ID, "loadingdefault")))
        primeiro_download_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "(//td[contains(@class, 'text-center')]//a[contains(@href, '.csv')])[1]"))
        )
        primeiro_download_link.click()
        download_dir = r'C:\Users\Junin\Downloads'
        destino = r'C:\Users\Junin\Desktop\dash\clientes'
        filename_fragment = 'leads'
        timeout = 60
        os.makedirs(destino, exist_ok=True)
        start_time = time.time()
        downloaded = False
        while time.time() - start_time < timeout:
            files = os.listdir(download_dir)
            print("Arquivos na pasta de download:", files)  # Debug
            for f in files:
                if filename_fragment in f.lower() and f.endswith('.csv'):
                    if f.endswith('.part') or f.endswith('.crdownload'):
                        continue
                    caminho_origem = os.path.join(download_dir, f)
                    caminho_destino = os.path.join(destino, f)
                    shutil.move(caminho_origem, caminho_destino)
                    downloaded = True
                    print(f"Arquivo encontrado e movido: {f}")
                    break
            if downloaded:
                break
            time.sleep(1)
        if not downloaded:
            print("Arquivo não foi encontrado ou não foi baixado dentro do tempo esperado.")
    except Exception as e:
        print(f"Erro no fluxo de exportação/baixa/movimentação: {e}")

if __name__ == "__main__":
    while True:
        print("Iniciando ciclo de automação...")
        fluxo_leads(driver, wait)
        fluxo_exporta_baixa_move(driver, wait)
        try:
            driver.get('https://crm.ipluc.com/')
            print("Retornou ao dashboard, pronto para novo ciclo.")
        except Exception as e:
            print(f"Erro ao voltar ao dashboard: {e}")
        print("Aguardando 20 segundos para novo ciclo...")
        time.sleep(20)

# Volta para a página inicial do dashboard antes de fechar o navegador
try:
    driver.get('https://crm.ipluc.com/')
    print("Retornou ao dashboard antes de fechar o navegador.")
except Exception as e:
    print(f"Erro ao voltar ao dashboard: {e}")

input("Pressione Enter para fechar o navegador...")
driver.quit()

while True:
    # --- Seu fluxo principal de automação ---
    # Exemplo: clicar menus, baixar arquivo, mover arquivo, etc.
    # ...
    
    # Volta para o dashboard
    try:
        driver.get('https://crm.ipluc.com/')
        print("Retornou ao dashboard, pronto para novo ciclo.")
    except Exception as e:
        print(f"Erro ao voltar ao dashboard: {e}")

    # Espera o tempo desejado antes de repetir o fluxo
    time.sleep(20)  