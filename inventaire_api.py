from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import bs4
import logging

logger = logging.getLogger('inventaire_api')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Define a custom user agent
my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
# Set up Chrome options
chrome_options = Options()
# Set the custom User-Agent
chrome_options.add_argument(f"--user-agent={my_user_agent}")
chrome_options.add_argument(f"--lang=es")
chrome_options.add_argument("--no-sandbox")
# Create a new instance of ChromeDriver with the desired options
driver = webdriver.Chrome(options=chrome_options)
logger.info("Created Driver")


def wait_until_loaded(by, selector):
    loaded = None
    while loaded is None:
        try:
            loaded = driver.find_element(by, selector)
        except:
            pass
    return True


def login(user, password):
    logger.info("Loggin..")
    driver.get("https://inventaire.io/login")
    wait_until_loaded(By.ID, 'username')
    _user = driver.find_element(By.ID, 'username')
    _pwd = driver.find_element(By.NAME, 'password')
    _show_pwd = driver.find_element(By.CLASS_NAME,
                                    'show-password.svelte-6g1eqi')
    _submit_button = driver.find_element(By.ID, 'login')
    _user.send_keys(user)
    _pwd.send_keys(password)
    _show_pwd.click()
    _submit_button.click()
    logged = None
    while logged is None:
        driver.implicitly_wait(1)
        try:
            logged = driver.find_element(
                By.CLASS_NAME, 'username.respect-case.svelte-19zdlyb')
            logger.info("Logging Success")
            return True
        except:
            pass
        try:
            logged = driver.find_element(By.CLASS_NAME,
                                         'flash.error.svelte-btfyjl')
            logger.info("Loging Failed")
            return False
        except:
            pass


def search_by_isbn(isbn):
    driver.get("https://inventaire.io")
    wait_until_loaded(By.XPATH, "//input[@class='svelte-qzi9hf']")
    logger.info("Search page loaded")
    _search_input = driver.find_element(By.XPATH,
                                        "//input[@class='svelte-qzi9hf']")
    _search_input.send_keys(isbn)
    search_result = None
    while search_result is None:
        driver.implicitly_wait(1)
        try:
            search_result = driver.find_element(By.CLASS_NAME, 'svelte-9gl3v7')
            logger.info("Search Success")
            _search_link = search_result.find_element(By.XPATH, "//a[@class='svelte-9gl3v7']")
            return _search_link.get_attribute('href')
        except:
            pass
        try:
            search_result = driver.find_element(By.CLASS_NAME,
                                                'no-result.svelte-qzi9hf')
            logger.info("Search Failed")
            return False
        except:
            pass


def create_work(title, author):
    driver.get("https://inventaire.io/entity/new?type=work")
    wait_until_loaded(By.CLASS_NAME, "column.svelte-1z0jooq")
    logger.info("Create work loaded")
    _title = driver.find_element(By.XPATH, "//input[@class='svelte-o6gvsq']")
    _title.send_keys(title)
    _save_button = driver.find_element(By.CLASS_NAME,
                                       'tiny-button.save.svelte-1lv9oa')
    _save_button.click()
    for elem in driver.find_elements(By.CLASS_NAME,
                                     "editor-section.svelte-1j1ofcl"):
        source = elem.get_attribute('innerHTML')
        if "Autor" in source:
            _author_button = elem.find_element(
                By.CLASS_NAME,
                'add-value.tiny-button.soft-grey.svelte-1j1ofcl')
            _author_element = elem
    _author_button.click()
    _author_input = _author_element.find_element(
        By.XPATH, "//input[@class='svelte-1u25yab']")
    _author_input.send_keys(author)
    wait_until_loaded(By.CLASS_NAME, 'svelte-dynnwx')
    logger.info("Author autocomplete loaded")
    _autocomplete = _author_element.find_element(
        By.CLASS_NAME, 'autocomplete.svelte-1u25yab')
    _author_found = False
    for auth in _autocomplete.find_elements(By.XPATH,
                                            "//li[@class='svelte-dynnwx']"):
        _author_name = (auth.find_element(
            By.CLASS_NAME,
            'label.svelte-dynnwx').get_attribute('innerHTML')).replace(
                'á',
                'a').replace('é',
                             'e').replace('í',
                                          'i').replace('ó',
                                                       'o').replace('ú', 'u')
        if _author_name in author:
            _author_found = True
            logger.info(f"Author {author} found")
            auth.click()
            break

    if not _author_found:
        loger.info(f"Author {author} not found, creating...")
        _autocomplete.find_element(By.CLASS_NAME,
                                   'create.svelte-1u25yab').click()
    logger.info("Author OK")
    _submit_work_button = driver.find_element(
        By.CLASS_NAME, 'light-blue-button.svelte-1z0jooq')
    _submit_work_button.click()
    logger.info("Submited")
    return True

