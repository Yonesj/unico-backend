import base64
from abc import ABC
from django.utils.translation import gettext_lazy as _
from playwright.sync_api import sync_playwright
from src.crawlers.captcha_solver.captcha_solver import solve


class GolestanBaseCrawler(ABC):
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def __navigate_to_login_page(self):
        """ Open the login page and wait for it to load. """
        self.page.goto("https://golestan.ui.ac.ir/forms/authenticateuser/main.htm")
        self.page.wait_for_load_state("load")

    def __extract_captcha(self):
        """ Extract the captcha image as a base64 string. """
        iframe_locator = self.page.frame_locator("iframe#Faci1")
        form_body_frame = iframe_locator.frame_locator("frame[name='Master']").frame_locator("frame[name='Form_Body']")
        captcha_element = form_body_frame.locator('img[id="imgCaptcha"]')
        captcha_byte = captcha_element.screenshot()
        return base64.b64encode(captcha_byte).decode("utf-8")

    def __submit_login(self, username, password, captcha_text):
        """ Fill in login details and submit the form. """
        iframe_locator = self.page.frame_locator("iframe#Faci1")
        form_body_frame = iframe_locator.frame_locator("frame[name='Master']").frame_locator("frame[name='Form_Body']")

        username_field = form_body_frame.locator('//*[@id="F80351"]')
        pass_field = form_body_frame.locator('//*[@id="F80401"]')
        captcha_field = form_body_frame.locator('//*[@id="F51701"]')

        username_field.fill(username)
        pass_field.fill(password)
        captcha_field.fill(captcha_text)

        # Click login button
        login_button = form_body_frame.locator('//*[@id="btnLog"]')
        login_button.click()
        self.page.wait_for_load_state("networkidle")

    def __check_login_status(self):
        """ Check if login was successful or failed (captcha or wrong password). """
        iframe_locator = self.page.frame_locator("iframe#Faci1")
        message_frame = iframe_locator.frame_locator("frame[name='Message']")
        max_tries = 20

        while max_tries > 0:
            if self.page.locator("iframe#Faci2").count() > 0:
                print("Login successful!")
                return True

            err_txt = message_frame.locator("#errtxt")
            error_message = err_txt.get_attribute("title")

            if error_message and error_message == "کد1 : شناسه کاربري يا گذرواژه اشتباه است.":
                raise ValueError(_("username or password is incorrect"))

            if error_message and error_message == "لطفا كد امنيتي را به صورت صحيح وارد نماييد":
                print("wrong_captcha")
                return False

            self.page.wait_for_timeout(100)
            max_tries -= 1

        raise Exception("unknown error")

    def login(self, username, password):
        """ Main function to login in golestan. """
        max_tries = 20

        while max_tries > 0:
            self.__navigate_to_login_page()
            captcha_b64 = self.__extract_captcha()

            try:
                captcha_text = solve(captcha_b64)
            except Exception:
                continue

            self.__submit_login(username, password, captcha_text)
            if self.__check_login_status():
                break

            max_tries -= 1

        if max_tries == 0:
            raise ValueError(_("Login failed"))

    def close(self):
        """ Clean up Playwright resources. """
        self.context.close()
        self.browser.close()
        self.playwright.stop()
