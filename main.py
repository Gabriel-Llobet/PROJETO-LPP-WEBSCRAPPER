import re
import time
import random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

from webdriver_manager.chrome import ChromeDriverManager



def main():
    driver = None

    try:
        # Recebe e valida o nick_tag.
        nick_tag = input_nick()
        print(f'Vamos buscar os dados de: {nick_tag}')

        # Separa o nick da tag para uso posterior.
        nick = separar_nick_tag(nick_tag)

        # Inicializa o WebDriver e configurações.
        driver = setup()

        # Navega até o site op.gg e realiza a pesquisa.
        navigate_to_opgg(driver)
        search_input(driver, nick_tag)

        # Seleciona a aba "Solo/Duo".
        soloduo_button(driver)
        
        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'button[value="FLEXRANKED"]'))
        )
        time_stamp = 0
        time_stamp_date = driver.find_element(By.CSS_SELECTOR, 'button[value="FLEXRANKED"]')
        
        random_sleep()
        
        

        # Botão "Flex" pode ser usado posteriormente.
        # flex_button(driver)

    except WebDriverException as e:
        print(f"Erro: {e}")
        raise SystemExit("Finalizando o programa.")
    finally:
        teardown(driver)



# Função para dormir por um tempo aleatório, evitando a identificação como bot.
def random_sleep():
    time.sleep(random.uniform(1, 3))


# Valida o formato do nick_tag informado para pesquisa.
def validar_nick_tag(nick: str) -> bool:
    padrao = r'^[\wÀ-ÿ\s]{3,16}#[\wÀ-ÿ\d]{3,5}$'
    if re.match(padrao, nick.strip()):
        print("Formato de nick e tag válido!")
        return True
    else:
        print("Formato inválido! Certifique-se de usar o formato: nome#tag.")
        return False


# Solicita e valida o nick_tag informado pelo usuário.
def input_nick():
    resultado = False
    while not resultado:
        nick_tag = input("Escreva nick e tag no seguinte formato: zezinho#br1\n")
        resultado = validar_nick_tag(nick_tag)
    return nick_tag


# Separa o nick da tag para uso posterior.
def separar_nick_tag(nick: str) -> str:
    return nick.split('#')[0]


# Configura o WebDriver do Chrome com as opções necessárias.
def setup(headless=False):
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

    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    else:
        options.add_argument("--start-fullscreen")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(3)
        driver.set_page_load_timeout(30)
        return driver
    except WebDriverException as e:
        print(f"Erro ao configurar o WebDriver: {e}")
        teardown()
        raise SystemExit("Finalizando o programa.")


# Navega até o site op.gg.
def navigate_to_opgg(driver):
    driver.get('https://www.op.gg/')


# Clica no botão de "Ranked Solo/Duo" na página.
def soloduo_button(driver):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[value="SOLORANKED"]'))
    )
    ranked_solo_duo_button = driver.find_element(By.CSS_SELECTOR, 'button[value="SOLORANKED"]')
    ranked_solo_duo_button.click()
    random_sleep()


# Clica no botão de "Ranked Flex" na página.
def flex_button(driver):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[value="FLEXRANKED"]'))
    )
    ranked_flex_button = driver.find_element(By.CSS_SELECTOR, 'button[value="FLEXRANKED"]')
    ranked_flex_button.click()
    random_sleep()


# Pesquisa o nick_tag informado na barra de pesquisa.
def search_input(driver, nick_tag):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "searchHome"))
    )
    text_box = driver.find_element(By.ID, "searchHome")
    text_box.send_keys(nick_tag)
    text_box.send_keys(Keys.RETURN)
    random_sleep()


# Finaliza o WebDriver e fecha o navegador.
def teardown(driver):
    if driver:
        driver.quit()


# Função principal que controla o fluxo do programa.
if __name__ == "__main__":
    main()