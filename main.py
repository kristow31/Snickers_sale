from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import os, time, base64
import csv
import requests
from loguru import logger

config_file = "config.ini"

if not os.path.exists(config_file):
    with open(config_file, "w") as file:
        file.write(
            "TELEGRAM_TOKEN = 0\n"
            "TELEGRAM_CHAT_ID = 0\n"
            "headless_chrome = 0\n"
            "path_chrome = chromedriver(94.0.4606.61).exe"
        )


def read_file(file_name):
    config = {}
    try:
        fh = open(file_name, "r")
        try:
            lines = fh.readlines()
            for l in lines:
                kv = l.strip().split(' = ')
                config[kv[0]] = kv[1]
        finally:
            fh.close()
    except IOError:
        print("Configuration file not found.")
    return config


CONFIG = read_file(config_file)

#logger.add('logs/debug.log', format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level="DEBUG", rotation="1 MB", compression="zip")


# options
options = webdriver.ChromeOptions()

# user-agent
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36")

# for ChromeDriver version 79.0.3945.16 or over
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("prefs", {
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# headless mode
options.headless = int(CONFIG['headless_chrome'])

driver = webdriver.Chrome(
    executable_path=CONFIG['path_chrome'],
    options=options
)

URL_site = "https://snickers.ru/hungerithm/"


def test(time_sleep=2, captcha=True):

    while True:

        driver.get(URL_site)
        time.sleep(2)

        logger.info("Run page...")
        el = '//div[@id="age-modal"]//a[@href="#"]'
        try:
            WebDriverWait(driver, 5).until(ec.visibility_of_element_located((By.XPATH, el)))
            logger.info("Закрываем AGE")
            driver.find_element_by_xpath(el).click()
        except:
            logger.info("Нет модального окна AGE")

        el = '//button[@id="onetrust-accept-btn-handler"]'
        try:
            WebDriverWait(driver, 5).until(ec.visibility_of_element_located((By.XPATH, el)))
            logger.info("Закрываем Куки")
            driver.find_element_by_xpath(el).click()
        except:
            logger.info("Нет модального окна Куки")

        el = '//span[@id="discount-1"]'
        try:
            WebDriverWait(driver, 60).until(ec.visibility_of_element_located((By.XPATH, el)))
            discount = driver.find_element_by_xpath(el).text
            logger.info("Текущая скидка {} %", discount)
        except:
            logger.info("Нет скидки")
            time.sleep(time_sleep)
            continue

        el = "//a[@href='#order']"
        try:
            WebDriverWait(driver, 60).until(ec.visibility_of_element_located((By.XPATH, el)))
            logger.info("Кнопка найдена")
            driver.find_element_by_xpath(el).click()
            time.sleep(2)
        except:
            logger.info("Нет первой кнопки")
            time.sleep(time_sleep)
            continue

        el = '//div[@class="order__subtitle text-center"]'
        try:
            WebDriverWait(driver, 5).until(ec.visibility_of_element_located((By.XPATH, el)))
            logger.info("Нет товара: {}", driver.find_element_by_xpath(el).text.replace("\n", " "))
            time.sleep(time_sleep)
            continue
        except:
            pass

        if captcha:
            el = '//div[@class="g-recaptcha"]'
            try:
                WebDriverWait(driver, 60).until(ec.visibility_of_element_located((By.XPATH, el)))
                logger.info("Каптча найдена")
                # 6LfLmLgUAAAAAAORbJmnPfTazf2wj1bhIFyFRHSi
                sitekey = driver.find_elements_by_xpath(el)[0].get_attribute('data-sitekey')
            except:
                logger.info("Ошибка Каптчи")
                time.sleep(time_sleep)
                continue

            try:
                rucaptcha_token = CONFIG['rucaptcha_token']
                logger.info("rucaptcha_token = {}", rucaptcha_token)
                logger.info(f'http://rucaptcha.com/in.php?key={rucaptcha_token}&method=userrecaptcha&googlekey={sitekey}&pageurl={URL_site}')
                html = requests.post(f'http://rucaptcha.com/in.php?key={rucaptcha_token}&method=userrecaptcha&googlekey={sitekey}&pageurl={URL_site}')
                logger.debug("sitekey status {} >> {}", html.status_code, html.text)
                if html.status_code != 200 or html.text.find('OK') == -1:
                    logger.error("Не верный запрос {} >> {}", html.status_code, html.text)
                else:
                    text = html.text.split('|')[1]
                    logger.info(f'http://rucaptcha.com/res.php?key={rucaptcha_token}&action=get&id={text}')
                    html = requests.get(f'http://rucaptcha.com/res.php?key={rucaptcha_token}&action=get&id={text}')
                    res = False
                    if html.status_code == 200 and html.text.find('OK|') != -1:
                        res = html.text.split('|')[1]
                    while res == False:
                        logger.info(f'ПОВТОР >> http://rucaptcha.com/res.php?key={rucaptcha_token}&action=get&id={text}')
                        html = requests.get(f'http://rucaptcha.com/res.php?key={rucaptcha_token}&action=get&id={text}')
                        if html.status_code == 200 and html.text.find('OK|') != -1:
                            res = html.text.split('|')[1]
                        logger.debug("sitekey status {} >> {}", html.status_code, html.text)
                        time.sleep(5)
            except:
                logger.info("Ошибка распознавания Каптчи")
                time.sleep(time_sleep)
                continue

            el = '//textarea[@id="g-recaptcha-response"]'
            try:
                WebDriverWait(driver, 60).until(ec.visibility_of_element_located((By.XPATH, el)))
                logger.info("textarea найдена")
                driver.execute_script("document.querySelector('#g-recaptcha-response').style.display = 'block'")
                driver.execute_script(f"document.querySelector('#g-recaptcha-response').innerText = '{res}'")
                time.sleep(5)
            except:
                logger.info("Ошибка textarea поле")
                time.sleep(time_sleep)
                continue

            el = "//a[@href='#order-2']"
            WebDriverWait(driver, 60).until(ec.visibility_of_element_located((By.XPATH, el)))
            logger.info("Решена каптча найдена")
            driver.find_element_by_xpath(el).click()
            res = False
            try:
                driver.wait_for_request('/hungerithm/backend/api/getCoupon', timeout=120)
                for request in driver.requests:
                    if 'getCoupon' in request.url:
                        logger.info('-----------------------------------------------------------------------------')
                        logger.info('URL >> {}', request.url)  # <--------------- Request url
                        logger.info('RESULT >> {}', request.response.body)
                        with open(os.path.basename(f'result.txt'), 'wb') as f:
                            f.write(request.response.body)
                        res = True
                        break
                del driver.requests
            except:
                logger.info("Ошибка получения кода от сервера")
                time.sleep(time_sleep)
                continue

        else:
            logger.debug("Ручной ввод каптчи")
            el = "//a[@href='#order-2']"
            WebDriverWait(driver, 120).until(ec.visibility_of_element_located((By.XPATH, el)))
            logger.info("Решена каптча найдена")
            driver.find_element_by_xpath(el).click()
            try:
                el = '//div[@class="bar__box"]'
                WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, el)))
                logger.info("Скриншот!")
                driver.find_element_by_xpath(el).screenshot('code.png')
                res = True
            except:
                try:
                    driver.wait_for_request('/hungerithm/backend/api/getCoupon', timeout=120)
                    for request in driver.requests:
                        if 'getCoupon' in request.url:
                            logger.info('-----------------------------------------------------------------------------')
                            logger.info('URL >> {}', request.url)  # <--------------- Request url
                            logger.info('RESULT >> {}', request.response.body)
                            with open(os.path.basename(f'result.txt'), 'wb') as f:
                                f.write(request.response.body)
                            res = True
                            break
                    del driver.requests
                except:
                    logger.info("Ошибка получения кода от сервера")
                    time.sleep(time_sleep)
                    continue

        if res:
            el = '//div[@class="bar__box"]'
            # скриншот


        logger.info("END programs")


def main():
    try:
        while True:

            driver.get(URL_site)
            time.sleep(2)

            logger.info("Run page...")
            el = '//div[@id="age-modal"]//a[@href="#"]'
            if WebDriverWait(driver, 5).until(ec.visibility_of_element_located((By.XPATH, el))):
                logger.info("Закрываем AGE")
                driver.find_element_by_xpath(el).click()

            el = '//button[@id="onetrust-accept-btn-handler"]'
            if WebDriverWait(driver, 5).until(ec.visibility_of_element_located((By.XPATH, el))):
                logger.info("Закрываем Куки")
                driver.find_element_by_xpath(el).click()

            WebDriverWait(driver, 60).until(ec.visibility_of_element_located((By.XPATH, "//a[@href='#order']")))
            logger.info("Кнопка найдена")
            driver.find_element_by_xpath("//a[@href='#order']").click()
            time.sleep(2)

            el = '//div[@class="order__subtitle text-center"]'
            WebDriverWait(driver, 5).until(ec.visibility_of_element_located((By.XPATH, el)))
            if len(driver.find_element_by_xpath(el)):
                logger.info("Нет товара: {}", driver.find_element_by_xpath(el).text.replace("\n", " "))
                time.sleep(3)
                continue
            '''
            el = "//div[@class='products__item slick-slide slick-cloned']"
            WebDriverWait(driver, 60).until(ec.visibility_of_element_located((By.XPATH, el)))
            logger.info("шоколадка найдена")
            driver.find_element_by_xpath(el).click()
            time.sleep(2)
            '''
            el = '//div[@class="g-recaptcha"]'
            WebDriverWait(driver, 60).until(ec.visibility_of_element_located((By.XPATH, el)))
            logger.info("Каптча найдена")
            sitekey = driver.find_elements_by_xpath(el)[0].get_attribute(
                'data-sitekey')  # 6LfLmLgUAAAAAAORbJmnPfTazf2wj1bhIFyFRHSi

            logger.info('http://rucaptcha.com/in.php?key=' + CONFIG[
                'rucaptcha_token'] + f'&method=userrecaptcha&googlekey={sitekey}&pageurl={URL_site}')
            html = requests.post('http://rucaptcha.com/in.php?key=' + CONFIG[
                'rucaptcha_token'] + f'&method=userrecaptcha&googlekey={sitekey}&pageurl={URL_site}')
            logger.debug("sitekey status {} >> {}", html.status_code, html.text)
            if html.status_code != 200 or html.text.find('OK') == -1:
                logger.error("Не верный запрос {} >> {}", html.status_code, html.text)
            else:
                text = html.text.split('|')[1]
                logger.info('http://rucaptcha.com/res.php?key=' + CONFIG['rucaptcha_token'] + f'&action=get&id={text}')
                html = requests.get(
                    'http://rucaptcha.com/res.php?key=' + CONFIG['rucaptcha_token'] + f'&action=get&id={text}')
                res = False
                if html.status_code != 200 or html.text.find('OK|') == -1:
                    res = html.text.split('|')[1]
                while not res:
                    logger.info(
                        'http://rucaptcha.com/res.php?key=' + CONFIG['rucaptcha_token'] + f'&action=get&id={text}')
                    html = requests.get(
                        'http://rucaptcha.com/res.php?key=' + CONFIG['rucaptcha_token'] + f'&action=get&id={text}')
                    if html.status_code != 200 or html.text.find('OK|') == -1:
                        res = html.text.split('|')[1]
                    logger.debug("sitekey status {} >> {}", html.status_code, html.text)
                    time.sleep(5)

            el = '//textarea[@id="g-recaptcha-response"]'
            WebDriverWait(driver, 60).until(ec.visibility_of_element_located((By.XPATH, el)))
            logger.info("textarea найдена")
            driver.execute_script("document.querySelector('#g-recaptcha-response').style.display = 'block'")
            driver.execute_script(f"document.querySelector('#g-recaptcha-response').innerText = '{res}'")
            time.sleep(5)

            el = "//a[@href='#order-2']"
            WebDriverWait(driver, 60).until(ec.visibility_of_element_located((By.XPATH, el)))
            logger.info("Решена каптча найдена")
            driver.find_element_by_xpath(el).click()

            request = driver.wait_for_request('/hungerithm/backend/api/getCoupon', timeout=120)
            for request in driver.requests:
                if 'getCoupon' in request.url:
                    logger.info('-----------------------------------------------------------------------------')
                    logger.info('URL >> {}', request.url)  # <--------------- Request url
                    logger.info('RESULT >> {}', request.response.body)
                    with open(os.path.basename(f'result.txt'), 'wb') as f:
                        f.write(request.response.body)
                    break
            del driver.requests

            if res:  # поменять
                el = '//div[@class="bar__box"]'
                # скриншот
                logger.info("Скриншот!")

            logger.info("END programs")

    except Exception as ex:
        logger.error("ERROR: {}", ex)
    finally:
        # driver.close()
        # driver.quit()
        logger.info("CLOSE Chrome")


if __name__ == "__main__":
    #main()
    test(time_sleep=10, captcha=False)
