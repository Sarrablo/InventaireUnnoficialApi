"""Inventaire unnoficial api"""
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from unidecode import unidecode


class InventaireApi:
    """Unnoficial Inventaire.io API"""

    def __init__(self):
        self.logger = logging.getLogger('inventaire_api')
        self.logger.setLevel(logging.DEBUG)
        st_ch = logging.StreamHandler()
        st_ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        st_ch.setFormatter(formatter)
        self.logger.addHandler(st_ch)

        self.my_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        )

        chrome_options = Options()
        chrome_options.add_argument(f"--user-agent={self.my_user_agent}")
        chrome_options.add_argument("--lang=es")
        chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.logger.info("Created Driver")

    def wait_until_loaded(self, by_selector, selector):
        """Wait unitl the desired element is loaded"""
        loaded = None
        while loaded is None:
            try:
                loaded = self.driver.find_element(by_selector, selector)
            except NoSuchElementException:
                pass
        return True

    def login(self, user, password):
        """Loggin into the inventaire web"""
        self.logger.info("Logging in...")
        self.driver.get("https://inventaire.io/login")
        self.wait_until_loaded(By.ID, 'username')

        _user = self.driver.find_element(By.ID, 'username')
        _pwd = self.driver.find_element(By.NAME, 'password')
        _show_pwd = self.driver.find_element(By.CLASS_NAME,
                                             'show-password.svelte-6g1eqi')
        _submit_button = self.driver.find_element(By.ID, 'login')

        _user.send_keys(user)
        _pwd.send_keys(password)
        _show_pwd.click()
        _submit_button.click()

        logged = None
        while logged is None:
            self.driver.implicitly_wait(1)
            try:
                logged = self.driver.find_element(
                    By.CLASS_NAME, 'username.respect-case.svelte-19zdlyb')
                self.logger.info("Login Success")
                return True
            except NoSuchElementException:
                pass
            try:
                logged = self.driver.find_element(By.CLASS_NAME,
                                                  'flash.error.svelte-btfyjl')
                self.logger.info("Login Failed")
                return False
            except NoSuchElementException:
                pass

    def search_by_isbn(self, isbn):
        """Find if a isbn exists in inventaire"""
        self.driver.get("https://inventaire.io")
        self.wait_until_loaded(By.XPATH, "/html/body/div/div[1]/nav/div[1]/input")
        self.logger.info("Search page loaded")

        _search_input = self.driver.find_element(
            By.XPATH, "/html/body/div/div[1]/nav/div[1]/input")
        _search_input.send_keys(isbn)

        search_result = None
        while search_result is None:
            self.driver.implicitly_wait(1)
            try:
                search_result = self.driver.find_element(
                    By.XPATH, '/html/body/div/div[1]/nav/div[1]/div[1]/div[2]/ul/li')
                self.logger.info("Search Success")
                _search_link = search_result.find_element(
                    By.XPATH, "a")
                return _search_link.get_attribute('href')
            except NoSuchElementException:
                pass
            try:
                search_result = self.driver.find_element(
                    By.XPATH, '/html/body/div/div[1]/nav/div[1]/div[1]/p')
                self.logger.info("Search Failed")
                return False
            except NoSuchElementException:
                pass

    def create_work(self, title, author, autosubmit=True):
        """Create a work (book)"""
        self.driver.get("https://inventaire.io/entity/new?type=work")
        self.wait_until_loaded(By.CLASS_NAME, "column.svelte-1z0jooq")
        self.logger.info("Create work loaded")

        _title = self.driver.find_element(By.XPATH,
                                          "//input[@class='svelte-o6gvsq']")
        _title.send_keys(title)

        _save_button = self.driver.find_element(
            By.CLASS_NAME, 'tiny-button.save.svelte-1lv9oa')
        _save_button.click()

        for elem in self.driver.find_elements(By.CLASS_NAME,
                                              "editor-section.svelte-1j1ofcl"):
            source = elem.get_attribute('innerHTML')
            if "Autor" in source:
                _author_button = elem.find_element(
                    By.CLASS_NAME,
                    'add-value.tiny-button.soft-grey.svelte-1j1ofcl')
                _author_element = elem
                break

        _author_button.click()
        _author_input = _author_element.find_element(
            By.XPATH, "//input[@class='svelte-1u25yab']")
        _author_input.send_keys(author)

        self.wait_until_loaded(By.CLASS_NAME, 'svelte-dynnwx')
        self.logger.info("Author autocomplete loaded")

        _autocomplete = _author_element.find_element(
            By.CLASS_NAME, 'autocomplete.svelte-1u25yab')
        _author_found = False

        for auth in _autocomplete.find_elements(
                By.XPATH, "//li[@class='svelte-dynnwx']"):
            _author_name = unidecode(
                auth.find_element(
                    By.CLASS_NAME,
                    'label.svelte-dynnwx').get_attribute('innerHTML'))
            if _author_name in author:
                _author_found = True
                self.logger.info("Author %s found", author)
                auth.click()
                break

        if not _author_found:
            self.logger.info("Author %s not found, creating...", author)
            _autocomplete.find_element(By.CLASS_NAME,
                                       'create.svelte-1u25yab').click()

        self.logger.info("Author OK")
        _submit_work_button = self.driver.find_element(
            By.CLASS_NAME, 'light-blue-button.svelte-1z0jooq')
        if autosubmit:
            _submit_work_button.click()
        self.logger.info("Submitted")
        return True

    def close(self):
        """Closing method"""
        self.driver.quit()
        self.logger.info("Driver closed")
