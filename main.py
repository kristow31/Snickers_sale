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


def main():

    try:
        driver.get("https://snickers.ru/hungerithm/")
        time.sleep(2)

        logger.info("Run page...")


        logger.info("END programs")





    except Exception as ex:
        logger.error("{}", ex)
    finally:
        driver.close()
        driver.quit()
        logger.info("CLOSE Chrome")


if __name__ == "__main__":
    main()
