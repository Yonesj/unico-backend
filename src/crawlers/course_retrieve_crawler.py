from .golestan_base_crawler import GolestanBaseCrawler


class CourseRetrieveCrawler(GolestanBaseCrawler):
    def __search_courses(self):
        """ Search for available courses using code 212. """
        iframe_locator2 = self.page.frame_locator("iframe#Faci2")
        form_body_frame2 = iframe_locator2.frame_locator("frame[name='Master']").frame_locator("frame[name='Form_Body']")

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

    def __extract_courses(self):
        """ Extract the course list from the page and return as structured data. """
        iframe_locator3 = self.page.frame_locator("iframe#Faci3")
        commander = iframe_locator3.frame_locator("frame[name='Commander']")

        with self.page.expect_popup() as new_tab_info:
            self.page.wait_for_timeout(100)
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
                'professor_name': course_data[9],
                'classes': course_data[10],
                'class_location': course_data[11],
                'prerequisites': course_data[12:-1],
                'notes': course_data[-1]
            })

        return student_course_data_list

    def fetch_student_courses(self, username, password):
        """ Main function to fetch student courses. """
        self.login(username, password)
        self.__search_courses()
        return self.__extract_courses()
