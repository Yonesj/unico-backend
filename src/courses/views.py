import base64

from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .serializers import GolestanRequestSerializer
from .student_courses_data import StudentCoursesData
from .captcha_solver import captcha_solver


def solve_and_handle(img_base64):
    solver = captcha_solver()
    response = solver.solve(base64_string)
    if response["status"] == "OK":
        captcha = response["captcha"]
        print("کپچا: ", captcha)
        return captcha
    else:
        error_message = response.get("message", "مشخص نیست")
        print("خطا: ", error_message)
        return None

class GetListCoursesView(GenericAPIView):
    """
    Get student courses list from Golestan.
    """
    serializer_class = GolestanRequestSerializer

    def get(self, request):
        serializer = GolestanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['student_id']
        password = serializer.validated_data['password']
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto("https://golestan.ui.ac.ir/forms/authenticateuser/main.htm")
            page.wait_for_load_state("load")
            ''' go to corroct frame and get captcha and username inputs'''
            iframe_locator = page.frame_locator("iframe#Faci1")
            master_frame = iframe_locator.frame_locator("frame[name='Master']")
            massage_frame = iframe_locator.frame_locator("frame[name='Message']")
            form_body_frame = master_frame.frame_locator("frame[name='Form_Body']")
            ''' getting captcha and solve it'''
            captcha_element = form_body_frame.locator('img[id="imgCaptcha"]')
            captcha_byte = captcha_element.screenshot()
            base64_string = base64.b64encode(captcha_byte).decode("utf-8")
            ''' fill username and captcha fields'''
            username_field = form_body_frame.locator('//*[@id="F80351"]')
            pass_field = form_body_frame.locator('//*[@id="F80401"]')
            captcha_field = form_body_frame.locator('//*[@id="F51701"]')

            captcha_text = solve_and_handle(base64_string)
            username_field.fill(username)
            pass_field.fill(password)
            captcha_field.fill(captcha_text)
            ''' login '''
            login_button = form_body_frame.locator('//*[@id="btnLog"]')
            login_button.click()
            page.wait_for_load_state("networkidle")

            '''
            After clicking the login button, an error might occur.
            This error could be a captcha error, which is quickly checked 
            And a response is returned, or it could be an incorrect username/password,
            which requires communication with the server to get the result.
            To handle this, we use a while loop that checks every 0.1 seconds
            whether an error has occurred.
            If no error occurs and the page progresses to the next step,
            the condition is met, and the loop exits. 
            However, if an error occurs (such as incorrect credentials or captcha error), 
            the correct response is sent back to the view accordingly.
            '''

            max_tries = 20
            while max_tries > 0:
                if page.locator("iframe#Faci2").count() > 0:
                    print("Login successful!")
                    break
                err_txt = massage_frame.locator("#errtxt")
                error_message = err_txt.get_attribute("title")
                if error_message:
                    if error_message == "کد1 : شناسه کاربري يا گذرواژه اشتباه است.":
                        return ("Wrong password")
                    elif error_message == "لطفا كد امنيتي را به صورت صحيح وارد نماييد":
                        return ("wrong captcha")
                page.wait_for_timeout(100)
                max_tries -= 1
            page.wait_for_load_state("load")
            iframe_locator2 = page.frame_locator("iframe#Faci2")
            master_frame2 = iframe_locator2.frame_locator("frame[name='Master']")
            form_body_frame2 = master_frame2.frame_locator("frame[name='Form_Body']")
            search_button = form_body_frame2.locator('//*[@id="F20851"]')
            '''
            fill search input with 212 code to get list of courses
            '''
            search_button.wait_for(state="visible")
            search_button.fill(str(212))
            search_click_button = form_body_frame2.locator('//*[@id="OK"]')
            search_click_button.wait_for(state="visible")

            '''
            click in serach button to go to courses list page.
            '''
            max_tries = 20
            while True:
                if max_tries == 0:
                    print("Error: Couldn't find the next page after multiple attempts.")
                    break
                search_click_button.click()
                page.wait_for_timeout(100)
                max_tries -= 1

            '''
            navigating to the correct frame to click on the "Show Table" button.
            '''
            iframe_locator3 = page.frame_locator("iframe#Faci3")
            commander = iframe_locator3.frame_locator("frame[name='Commander']")
            with page.expect_popup() as new_tab_info:
                commander.locator('//*[@id="ExToEx"]').click()
            course_page = new_tab_info.value
            course_page.wait_for_selector("table")
            main_table = course_page.locator("table").first
            rows = main_table.locator("> tbody > tr")
            ''' Get all data '''
            all_data = rows.all_inner_texts()
            student_course_data_list = []
            for course in all_data:
                course_data = course.split('\t')
                student_id = course_data[0]
                full_name = course_data[1]
                course_code = course_data[3]
                course_name = course_data[4]
                theory = course_data[5]
                practical = course_data[6]
                capacity = course_data[7]
                gender = course_data[8]
                professor = course_data[9]
                class_day = course_data[10]
                class_location = course_data[11]
                prerequisites = course_data[12:-1]
                notes = course_data[-1]
                student_course_data = StudentCoursesData(student_id, full_name, course_code, course_name, theory,
                                                         practical, capacity, gender, professor, class_day,
                                                         class_location, prerequisites, notes)
                student_course_data_list.append(student_course_data.to_dict())
        finally:
            context.close()
            browser.close()



        # return Response({'image': captcha_image_base64}, status=status.HTTP_200_OK)

        # try:
        #     activation_obj = ActivationCode.objects.get(code=code)
        # except ActivationCode.DoesNotExist:
        #     return Response({'detail': 'Invalid activation code.'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # user = activation_obj.user
        #
        # if user.is_active:
        #     return Response({'detail': 'User is already activated.'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # now = timezone.now()
        # if not activation_obj.created_at or now > activation_obj.created_at + timedelta(minutes=10):
        #     return Response({'detail': 'Activation code has expired.'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # user.is_active = True
        # user.save(update_fields=['is_active'])
        # activation_obj.delete()
        #
        # return Response({'detail': 'User activated successfully.'}, status=status.HTTP_200_OK)
