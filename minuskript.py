import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def main():
    # --- BRAUSERI SEADISTAMINE CAPTCHA VÄLTIMISEKS ---
    options = webdriver.ChromeOptions()

    # Peidame automaatika tunnused
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Määrame tavalise inimese User-Agenti
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    # Täiendav skript, mis kustutab "I am a robot" märke brauseri mälust
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    try:
        # 1. Avame Google'i avalehe
        print("[Samm 1/7] Avame Google'i avalehe...")
        driver.get("https://www.google.com")
        time.sleep(random.uniform(1.5, 2.5))  # Inimlik paus

        # --- NÕUSOLEKUAKEN (Küpsised) ---
        print("[Samm 2/7] Kontrollime küpsiste akna olemasolu...")
        try:
            accept_button = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//button[contains(., 'Nõustu kõigiga') or contains(., 'Accept all') or contains(., 'I agree') or @id='L2AGLb']"
                                            ))
            )
            driver.execute_script("arguments[0].click();", accept_button)
            print(" -> Küpsiste aken edukalt suletud.")
            time.sleep(random.uniform(1.0, 2.0))
        except TimeoutException:
            print(" -> Küpsiste akent ei kuvatud, jätkame.")

        # --- OTSINGUKASTI LEIDMINE ---
        print("[Samm 3/7] Otsime otsingukasti...")
        search_box = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.NAME, "q"))
        )

        query = "Selenium automation testing"
        search_box.clear()

        # Simuleerime trükkimist väikese viivitusega, mitte ei kleebi teksti ühe korraga
        for char in query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

        time.sleep(0.5)
        search_box.send_keys(Keys.ENTER)
        print(f" -> Päring '{query}' sisestatud ja käivitatud.")

        # Kontrollime, kas sattusime CAPTCHA otsa
        if "captcha" in driver.current_url.lower() or "sorry" in driver.current_url.lower():
            print(
                "\n[HOIATUS] Google kuvas ikkagi CAPTCHA! Palun lahenda see brauseriaknas käsitsi, test ootab 30 sekundit...")
            time.sleep(30)  # Annab sulle aega brauseris linnuke ise ära klikkida

        # Ootame kindlalt tulemuste konteineri ilmumist
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        time.sleep(1.5)

        # --- ESIMESE TULEMUSE KLIKKIMINE ---
        print("[Samm 4/7] Otsime esimest reaalset otsingutulemust...")
        try:
            first_link = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, "(//div[@id='search']//a[h3])[1]"))
            )
            print(f" -> Klikime tulemusel...")
            driver.execute_script("arguments[0].click();", first_link)

            time.sleep(random.uniform(3.0, 4.0))  # Ootame sihtlehel nagu inimene
            driver.back()
            print(" -> Navigeeriti tagasi Google'i tulemustesse.")

            WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.ID, "search")))
        except Exception as e:
            print(f" [HOIATUS] Otsingulinki ei saanud klikkida: {e}")

        # --- PAGINATSIOON ---
        print("[Samm 5/7] Kerime lehe alla...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

        print("[Samm 6/7] Üritame liikuda järgmisele lehele...")
        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//*[@id='pnnext'] | //a[contains(@aria-label, 'Next page') or contains(., 'Järgmine')]"))
            )
            driver.execute_script("arguments[0].click();", next_button)
            print(" -> Teine lehekülg edukalt laetud!")
            time.sleep(3)
        except TimeoutException:
            print(" [HOIATUS] Järgmise lehe nuppu ei leitud (tõenäoliselt on kasutusel lõputu kerimine).")

        print("[Samm 7/7] Testtsükkel edukalt läbitud.")

    except Exception as e:
        print(f"\n[KRIITILINE VIGA] Test katkes ootamatult: {e}")

    finally:
        print("Sulgeme brauseri.")
        driver.quit()


if __name__ == "__main__":
    main()