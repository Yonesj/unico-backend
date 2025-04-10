import time


class UserGolestanValidator:
    def user_validator(self, page):
        # Navigate to student info section
        iframe2 = page.frame_locator("iframe#Faci2")
        form_body2 = iframe2.frame_locator("frame[name='Master']").frame_locator("frame[name='Form_Body']")
        student_info_btn = form_body2.locator('//td[span[text()="اطلاعات جامع دانشجو"]]')
        student_info_btn.wait_for(state="visible", timeout=5000)
        student_info_btn.click()
        time.sleep(0.5)
        student_info_btn.click()

        iframe3 = page.frame_locator("iframe#Faci3")
        form_body3 = iframe3.frame_locator("frame[name='Master']").frame_locator("frame[name='Form_Body']")

        student_name_el = form_body3.locator('label#F51851')
        student_number_el = form_body3.locator('input#F41251')
        student_major_el = form_body3.locator('//*[@id="F17551"]')
        student_faculty_el = form_body3.locator('//*[@id="F61151"]')

        student_name_el.wait_for(state="visible", timeout=5000)
        student_number_el.wait_for(state="visible", timeout=5000)
        student_major_el.wait_for(state="visible", timeout=5000)
        student_faculty_el.wait_for(state="visible", timeout=5000)

        student_fullname = student_name_el.text_content()
        student_number = student_number_el.input_value()
        major = student_major_el.text_content()
        faculty = student_faculty_el.text_content()


        return {
            "student_number": student_number,
            "full_name": student_fullname,
            "major": major,
            "faculty": faculty
        }
