"""Inventaire unnoficial api"""
import logging
import time
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
        _show_pwd = self.driver.find_element(
            By.XPATH,
            '/html/body/div/main/div/div/form/div[2]/div/label/input')
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
                    By.XPATH,
                    '/html/body/div/main/div/div/div[2]/div[1]/div[1]/div[2]/h2'
                )
                self.logger.info("Login Success")
                return True
            except NoSuchElementException:
                pass
            try:
                logged = self.driver.find_element(
                    By.XPATH, '/html/body/div/main/div/div/form/div[3]/div/i')
                self.logger.info("Login Failed")
                return False
            except NoSuchElementException:
                pass

    def search_by_isbn(self, isbn):
        """Find if a isbn exists in inventaire"""
        self.driver.get("https://inventaire.io")
        self.wait_until_loaded(By.XPATH,
                               "/html/body/div/div[1]/nav/div[1]/input")
        self.logger.info("Search page loaded")

        _search_input = self.driver.find_element(
            By.XPATH, "/html/body/div/div[1]/nav/div[1]/input")
        _search_input.send_keys(isbn)

        search_result = None
        while search_result is None:
            self.driver.implicitly_wait(1)
            try:
                search_result = self.driver.find_element(
                    By.XPATH,
                    '/html/body/div/div[1]/nav/div[1]/div[1]/div[2]/ul/li')
                self.logger.info("Search Success")
                _search_link = search_result.find_element(By.XPATH, "a")
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
        self.wait_until_loaded(By.XPATH,
                               "/html/body/div/main/div/div[3]/button/i")
        self.logger.info("Create work loaded")

        _title = self.driver.find_element(
            By.XPATH, "/html/body/div/main/div/div[2]/div/div/div[1]/input")
        _title.send_keys(title)

        _save_button = self.driver.find_element(
            By.XPATH,
            '/html/body/div/main/div/div[2]/div/div/div[2]/button[1]')
        _save_button.click()

        _add_author_button = self.driver.find_element(
            By.XPATH, "/html/body/div/main/div/li[2]/div/button/i")
        _add_author_button.click()
        _author_input = self.driver.find_element(
            By.XPATH,
            "/html/body/div/main/div/li[2]/div/div/div[1]/div[1]/div/input")
        _author_input.send_keys(author)

        self.wait_until_loaded(By.XPATH,
                               "//div[starts-with(@class,'autocomplete')]")
        self.logger.info("Author autocomplete loaded")
        _author_element = self.driver.find_element(
            By.XPATH, "/html/body/div/main/div/li[2]")
        _autocomplete = _author_element.find_element(
            By.XPATH, "//div[starts-with(@class,'autocomplete')]")
        _author_found = False

        for auth in _autocomplete.find_elements(
                By.XPATH, "//li[starts-with(@class,'svelte')]"):
            _author_name = unidecode(
                auth.find_element(
                    By.XPATH,
                    "//span[starts-with(@class,'label')]").get_attribute(
                        'innerHTML'))
            if _author_name in author:
                _author_found = True
                self.logger.info("Author %s found", author)
                auth.click()
                break

        if not _author_found:
            self.logger.info("Author %s not found, creating...", author)
            _autocomplete.find_element(
                By.XPATH, "//button[starts-with(@class,'create')]").click()

        self.logger.info("Author OK")
        _submit_work_button = self.driver.find_element(
            By.XPATH, '//*[@id="main"]/div/div[3]/button')
        if autosubmit:
            _submit_work_button.click()
        self.logger.info("Submitted")
        return True

    def create_edition(self, parent, isbn):
        """Create edition for an specified work"""
        self.driver.get(parent)
        self.wait_until_loaded(
            By.XPATH,
            '/html/body/div/main/div/div[2]/div/div[1]/div[2]/div/div[1]/h5')
        self.logger.info("Adding %s edition", isbn)
        _add_edition_button = self.driver.find_element(
            By.XPATH, ('/html/body/div/main/div/div[2]/div/div[1]/div[2]'
                       '//button[starts-with(@class,"tiny-button")]'))
        _add_edition_button.click()
        _edition_input = self.driver.find_element(
            By.XPATH,
            ("/html/body/div/main/div/div[2]/div/div[1]/div[2]"
             "//input[starts-with(@class, 'has-alertbox enterClick')]"))
        _edition_input.send_keys(isbn)
        _submit_add_edition = self.driver.find_element(
            By.XPATH, ("/html/body/div/main/div/div[2]/div/div[1]/div[2]"
                       "//button[starts-with(@class,'isbn-button')]"))
        _submit_add_edition.click()
        addition_result = None
        while addition_result is None:
            self.driver.implicitly_wait(1)
            try:
                addition_result = self.driver.find_element(
                    By.XPATH,
                    ('/html/body/div/main/div/div[2]/div/div[1]/div/div'
                     '/div[1]/div[2]/div/div[2]'
                     '//span[starts-with(@class, "property")]'))
                self.logger.info("Adition Success")
                return True
            except NoSuchElementException:
                pass
            try:
                addition_result = self.driver.find_element(
                    By.XPATH,
                    '//*[@id="main"]/div/div[2]/div/div[1]/div[2]/div/div[4]/div[2]/div/i'
                )
                self.logger.info("Adition Failed (Alredy exists)")
                return False
            except NoSuchElementException:
                pass

    def edit_edition(self,
                     isbn,
                     image=None,
                     pages=None,
                     publisher=None,
                     collection=None,
                     date=None):
        """Add data to an edition"""
        if not (_edition_url := self.search_by_isbn(isbn)):
            self.logger.info("Edition %s not found, create first", isbn)
            return False
        self.driver.get(f"{_edition_url}/edit")
        self.wait_until_loaded(
            By.XPATH, "/html/body/div/main/div/ul/li[1]/div/div/div/button")
        self.logger.info("Edit page for %s loaded", isbn)
        #Add image
        if image:
            try:
                #Find if the edition has not an image
                _add_image_button = self.driver.find_element(
                    By.XPATH,
                    "/html/body/div/main/div/ul/li[6]/div/button/span")
                _new_image = True
            except NoSuchElementException:
                #It has an image, edit it
                _new_image = False
                _add_image_button = self.driver.find_element(
                    By.XPATH,
                    "/html/body/div/main/div/ul/li[6]/div/div/div/div/button/i"
                )
            _add_image_button.click()
            _image_input = self.driver.find_element(
                By.XPATH,
                "/html/body/div/main/div/ul/li[6]/div/div/div/div[1]/label[1]/input"
            )
            _image_input.send_keys(image)
            if _new_image:
                self.wait_until_loaded(
                    By.XPATH,
                    "/html/body/div/main/div/ul/li[6]/div/div/div/div[1]/div[2]/button[1]/i"
                )
            else:
                #I dont like this solution but i dont know how to control the new load
                time.sleep(2)
            self.logger.info("Image loaded")
            _save_image_btn = self.driver.find_element(
                By.XPATH,
                "/html/body/div/main/div/ul/li[6]/div/div/div/div[2]/button[1]"
            )
            _save_image_btn.click()
            self.logger.info("Image saved")
        if date:
            _date_button = self.driver.find_element(
                By.XPATH,
                "/html/body/div/main/div/ul/li[11]/div/div/div/div/button")
            _date_button.click()
            _year_input = self.driver.find_element(
                By.XPATH, '//*[@id="component24-year"]')
            _year_input.clear()
            _year_input.send_keys(date.year)
            try:
                _month_button = self.driver.find_element(
                    By.XPATH,
                    "/html/body/div/main/div/ul/li[11]/div/div/div/div[1]/div[2]/button[1]"
                )
                _month_button.click()
            except NoSuchElementException:
                pass
            _month_input = self.driver.find_element(
                By.XPATH, '//*[@id="component24-month"]')
            _month_input.clear()
            _month_input.send_keys(date.month)
            _save_date_btn = self.driver.find_element(
                By.XPATH,
                "/html/body/div/main/div/ul/li[11]/div/div/div/div[2]/button[1]"
            )
            _save_date_btn.click()

        if pages:
            _pages_button = self.driver.find_element(
                By.XPATH,
                "/html/body/div/main/div/ul/li[14]/div/div/div/div/button/i")
            _pages_button.click()
            _pages_input = self.driver.find_element(
                By.XPATH,
                "/html/body/div/main/div/ul/li[14]/div/div/div/input")
            _pages_input.clear()
            _pages_input.send_keys(pages)
            _save_pages_btn = self.driver.find_element(
                By.XPATH,
                "/html/body/div/main/div/ul/li[14]/div/div/div/div/button[1]")
            _save_pages_btn.click()
            self.logger.info("Pages saved")
        if publisher:
            _publisher_button = self.driver.find_element(
                By.XPATH, "/html/body/div/main/div/ul/li[7]/div/button/i")
            _publisher_button.click()
            _publisher_input = self.driver.find_element(
                By.XPATH,
                "/html/body/div/main/div/ul/li[7]/div/div/div/div[1]/div/input"
            )
            _publisher_input.clear()
            _publisher_input.send_keys(publisher)
            _publisher_element = self.driver.find_element(
                By.XPATH, "/html/body/div/main/div/ul/li[7]")
            self.driver.implicitly_wait(1)

            _autocomplete = _publisher_element.find_element(
                By.XPATH, "//div[starts-with(@class,'autocomplete')]")

            _publisher_found = False

            self.driver.implicitly_wait(2)
            for _publis in _autocomplete.find_elements(
                    By.XPATH, "//li[starts-with(@class,'svelte')]"):
                _publisher_name = unidecode(
                    _publis.find_element(
                        By.XPATH,
                        ".//span[starts-with(@class,'label')]").get_attribute(
                            'innerHTML'))
                if _publisher_name in publisher:
                    _publisher_found = True
                    self.logger.info("Publisher %s found", publisher)
                    _publis.click()
                    break

            if not _publisher_found:
                self.logger.info("Publisher %s not found, creating...",
                                 publisher)
                _autocomplete.find_element(
                    By.XPATH,
                    "//button[starts-with(@class,'create')]").click()

            input()

    def close(self):
        """Closing method"""
        self.driver.quit()
        self.logger.info("Driver closed")
