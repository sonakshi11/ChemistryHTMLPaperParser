import os
import time

try:
    import pyautogui
    import shutil
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.webdriver import WebDriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import WebDriverException, NoSuchElementException
except KeyError:
    pass

from .constants import *
from seqlbtoolkit.text import substring_mapping


def scroll_down(driver_var, value):
    driver_var.execute_script("window.scrollBy(0," + str(value) + ")")


# Scroll down the page
def scroll_down_page(driver, n_max_try=100):

    old_page = driver.page_source
    for _ in range(n_max_try):
        for i in range(2):
            scroll_down(driver, 500)
            time.sleep(0.1)
        new_page = driver.page_source
        if new_page != old_page:
            old_page = new_page
        else:
            break
    return True


def every_downloads_chrome(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        var items = document.querySelector('downloads-manager')
            .shadowRoot.getElementById('downloadsList').items;
        if (items.every(e => e.state === "COMPLETE"))
            return items.map(e => e.fileUrl || e.file_url);
        """)


def download_article_windows(doi, download_path):

    article_url = 'https://doi.org/' + doi
    driver = load_webdriver()

    driver.get(article_url)
    scroll_down_page(driver)

    if doi.startswith('10.1039'):
        try:
            driver.find_element(By.LINK_TEXT, 'Article HTML').click()
            scroll_down_page(driver)
        except NoSuchElementException:
            pass

    pyautogui.hotkey('ctrl', 's')

    time.sleep(1)

    file_name = substring_mapping(doi, CHAR_TO_HTML_LBS) + '.html'
    save_path = os.path.join(download_path, file_name)
    save_path = os.path.abspath(os.path.normpath(save_path))

    if os.path.isfile(save_path):
        os.remove(save_path)
    if os.path.isdir(save_path.replace('.html', '_files')):
        shutil.rmtree(save_path.replace('.html', '_files'))
    pyautogui.write(save_path)
    pyautogui.hotkey('enter')
    time.sleep(0.1)

    pyautogui.hotkey('ctrl', 't')
    time.sleep(0.1)
    driver.switch_to.window(driver.window_handles[1])
    _ = WebDriverWait(driver, 120, 1).until(every_downloads_chrome)
    time.sleep(0.1)

    driver.quit()


def download_article_headless(doi, save_path):

    article_url = 'https://doi.org/' + doi
    driver = load_webdriver()

    driver.get(article_url)


def load_webdriver() -> WebDriver:
    """
    A more robust way to load chrome webdriver (compatible with headless mode)

    Returns
    -------
    WebDriver
    """
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    except WebDriverException:
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    return driver