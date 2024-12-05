# Importação de bibliotecas necessárias
import re
import time
import random
import pandas as pd

# Importação do Selenium e seus módulos
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

# Gerenciador do driver do Chrome
from webdriver_manager.chrome import ChromeDriverManager

# Função principal que controla o fluxo do programa
def main():

    try:
        # Solicita o nick_tag do usuário e valida
        nick_tag = input_nick()
        print(f'Buscando dados de: {nick_tag}')

        # Separa apenas o "nick" para uso posterior
        nick = separar_nick_tag(nick_tag)

        # Configura o WebDriver
        driver = setup()

        # Navega até o site op.gg e realiza a pesquisa pelo nick_tag
        navigate_to_opgg(driver)
        search_input(driver, nick_tag)

        # Seleciona a aba "Ranked Solo/Duo"
        soloduo_button(driver)

        # Coleta informações das partidas
        match_divs = driver.find_elements(By.CLASS_NAME, "css-j7qwjs")
        dados_partidas = []

        # Itera por cada partida encontrada
        for match in match_divs:
            partida = extrair_dados_partida(match)  # Função para extração de dados
            dados_partidas.append(partida)

        print(f'Total de partidas encontradas: {len(dados_partidas)}')

        # Exibe os dados extraídos
        for partida in dados_partidas:
            print(partida)

        # Salva os dados em formato CSV
        salvar_dados_csv(dados_partidas, nick)

    except WebDriverException as e:
        print(f"Erro: {e}")
        raise SystemExit("Finalizando o programa.")
    finally:
        # Garante que o WebDriver será encerrado
        teardown(driver)

# Função para dormir por um tempo aleatório (anti-bot)
def random_sleep():
    time.sleep(random.uniform(1, 3))

# Valida o formato do nick_tag
def validar_nick_tag(nick: str) -> bool:
    padrao = r'^[\wÀ-ÿ\s]{3,16}#[\wÀ-ÿ\d]{3,5}$'
    if re.match(padrao, nick.strip()):
        print("Formato de nick e tag válido!")
        return True
    else:
        print("Formato inválido! Use: nome#tag.")
        return False

# Solicita e valida o nick_tag informado pelo usuário
def input_nick():
    while True:
        nick_tag = input("Digite o nick e tag no formato: nome#tag\n")
        if validar_nick_tag(nick_tag):
            return nick_tag

# Separa o nick da tag
def separar_nick_tag(nick: str) -> str:
    return nick.split('#')[0]

# Configura o WebDriver
def setup():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("window-size=1920x1080")
    options.add_argument("--log-level=3")
    options.accept_insecure_certs = True
    options.page_load_strategy = 'eager'

    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.ads": 2
    }
    options.add_experimental_option("prefs", prefs)

    #Modo headless não está funcional.    
    #if headless:
        #options.add_argument("--headless")
        #options.add_argument("--disable-gpu")
    
    options.add_argument("--start-fullscreen")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(3)
        driver.set_page_load_timeout(30)
        return driver
    except WebDriverException as e:
        print(f"Erro ao configurar o WebDriver: {e}")
        teardown(driver)
        raise SystemExit("Finalizando o programa.")

# Navega até o site op.gg
def navigate_to_opgg(driver):
    driver.get('https://www.op.gg/')

# Seleciona a aba "Ranked Solo/Duo"
def soloduo_button(driver):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[value="SOLORANKED"]'))
    ).click()
    random_sleep()

# Pesquisa o nick_tag na barra de busca
def search_input(driver, nick_tag):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "searchHome"))
    ).send_keys(nick_tag + Keys.RETURN)
    random_sleep()

# Extrai os dados de uma partida
def extrair_dados_partida(match):
    partida = {
        "Tipo de partida": match.find_element(By.CLASS_NAME, "game-type").text,
        "Horário": match.find_element(By.CLASS_NAME, "time-stamp").text,
        "Resultado": match.find_element(By.CLASS_NAME, "result").text,
        "Duração": match.find_element(By.CLASS_NAME, "length").text,
        "Jogador Alvo Nome": match.find_element(By.CLASS_NAME, "is-me").find_element(By.CLASS_NAME, "summoner-tooltip").text,
        "Jogador Alvo Campeão": match.find_element(By.CLASS_NAME, "is-me").find_element(By.TAG_NAME, "img").get_attribute("alt"),
        "Rota": match.find_element(By.CLASS_NAME, "laning--my").text,
        "KDA": match.find_element(By.CLASS_NAME, "kda").text,
        "KDA Ratio": match.find_element(By.CLASS_NAME, "kda-ratio").text,
        "P/Kill": match.find_element(By.CLASS_NAME, "p-kill").text,
        "CS": match.find_element(By.CLASS_NAME, "cs").text,
        "Rank Médio da Partida": match.find_element(By.CLASS_NAME, "avg-tier").text,
    }
    return partida

# Salva os dados em formato CSV
def salvar_dados_csv(dados_partidas, nick):
    df = pd.DataFrame(dados_partidas)
    arquivo = f"{nick}_dados_partidas.csv"
    df.to_csv(arquivo, index=False)
    print(f'Dados salvos em: {arquivo}')

# Finaliza o WebDriver
def teardown(driver):
    if driver:
        driver.quit()

# Executa o programa
if __name__ == "__main__":
    main()
