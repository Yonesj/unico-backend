import base64
from playwright.sync_api import sync_playwright
from .captcha_solver.captcha_solver import solve


class Crawler:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def navigate_to_login_page(self):
        """ Open the login page and wait for it to load. """
        self.page.goto("https://golestan.ui.ac.ir/forms/authenticateuser/main.htm")
        self.page.wait_for_load_state("load")

    def extract_captcha(self):
        """ Extract the captcha image as a base64 string. """
        iframe_locator = self.page.frame_locator("iframe#Faci1")
        form_body_frame = iframe_locator.frame_locator("frame[name='Master']").frame_locator("frame[name='Form_Body']")
        captcha_element = form_body_frame.locator('img[id="imgCaptcha"]')
        captcha_byte = captcha_element.screenshot()
        return base64.b64encode(captcha_byte).decode("utf-8")

    def submit_login(self, username, password, captcha_text):
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

    def check_login_status(self):
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
                raise ValueError("username or password is incorrect")

            if error_message and error_message == "لطفا كد امنيتي را به صورت صحيح وارد نماييد":
                print("wrong_captcha")
                return False

            self.page.wait_for_timeout(100)
            max_tries -= 1

        raise Exception("unknown error")

    def search_courses(self):
        """ Search for available courses using code 212. """
        iframe_locator2 = self.page.frame_locator("iframe#Faci2")
        form_body_frame2 = iframe_locator2.frame_locator("frame[name='Master']").frame_locator(
            "frame[name='Form_Body']")

        search_button = form_body_frame2.locator('//*[@id="F20851"]')
        search_button.wait_for(state="visible")
        search_button.fill("212")

        search_click_button = form_body_frame2.locator('//*[@id="OK"]')
        search_click_button.wait_for(state="visible")
        max_tries = 20

        while max_tries > 0:
            if self.page.locator("iframe#Faci3").count() > 0:
                return
            search_click_button.click()
            self.page.wait_for_timeout(100)
            max_tries -= 1

        raise Exception("Couldn't find the 212 report page after multiple attempts.")

    def extract_courses(self):
        """ Extract the course list from the page and return as structured data. """
        iframe_locator3 = self.page.frame_locator("iframe#Faci3")
        commander = iframe_locator3.frame_locator("frame[name='Commander']")

        with self.page.expect_popup() as new_tab_info:
            commander.locator('//*[@id="ExToEx"]').click()
        course_page = new_tab_info.value

        course_page.wait_for_selector("table")
        main_table = course_page.locator("table").first
        rows = main_table.locator("> tbody > tr")
        all_data = rows.all_inner_texts()
        student_course_data_list = []

        for i in range(1, len(all_data)):
            course_data = all_data[i].split('\t')
            student_course_data_list.append({
                'course_code': course_data[3],
                'course_name': course_data[4],
                'theory': course_data[5],
                'practical': course_data[6],
                'capacity': course_data[7],
                'gender': course_data[8],
                'professor_name': course_data[9].strip(),
                'classes': course_data[10],
                'class_location': course_data[11].strip(),
                'prerequisites': course_data[12:-1],
                'notes': course_data[-1]
            })

        return student_course_data_list

    def fetch_student_courses(self, username, password):
        """ Main function to fetch student courses. """
        max_tries = 20

        while max_tries > 0:
            self.navigate_to_login_page()
            captcha_b64 = self.extract_captcha()

            try:
                captcha_text = solve(captcha_b64)
            except Exception:
                continue

            self.submit_login(username, password, captcha_text)
            if self.check_login_status():
                break

            max_tries -= 1

        if max_tries == 0:
            raise ValueError("Login failed")

        self.search_courses()
        return self.extract_courses()

    def close(self):
        """ Clean up Playwright resources. """
        self.context.close()
        self.browser.close()
        self.playwright.stop()
