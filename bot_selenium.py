import os

import ddddocr
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from PIL import Image

# 提供ChromeDriver可执行文件的路径
CHROMEDRIVER_PATH = r"C:\Users\chenhao3.vendor\.chromium-browser-snapshots\chromium\win64-12766661\chrome-win\chrome.exe"


def solve_captcha(driver, idx):

    # 等待滑块元素可见
    try:
        for i in range(3):

            # 使用Selenium实现验证码解决逻辑
            iframe = None
            try:
                iframe = WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'iframe[name="https://t.captcha.qq.com"]')))
            except Exception as e:
                print("not found captcha dom")
                return

            # 切换到iframe上下文
            driver.switch_to.frame(iframe)

            puzzle = None
            slider_elements = WebDriverWait(driver, 2).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.tc-fg-item')))
            for element in slider_elements:
                style = element.get_attribute('style')
                if 'background-image' in style and 'background-position: 0px' not in style:
                    puzzle = element
                    slider_url = style.split('url("')[1].split('")')[0]
                    with open('slider_tmp' + str(idx) + '.png', 'wb') as f1:
                        f1.write(requests.get(slider_url).content)
                    print("滑块图片URL:", slider_url)
                    image = Image.open('slider_tmp' + str(idx) + '.png')

                    cropped_image = image.crop((140, 495, 260, 610))

                    # 保存裁剪后的图片
                    cropped_image.save('slider_' + str(idx) + '.png')

            bg_element = WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#slideBgWrap > div')))
            bg_style = bg_element.get_attribute('style')
            bg_url = bg_style.split('url("')[1].split('")')[0]
            with open('bg_' + str(idx) + '.png', 'wb') as f2:
                f2.write(requests.get(bg_url).content)
            print("背景图片URL:", bg_url)

            #
            det = ddddocr.DdddOcr(det=False, ocr=False)
            target_bytes = None
            background_bytes = None
            with open('slider_' + str(idx) + '.png', 'rb') as f:
                target_bytes = f.read()

            with open('bg_' + str(idx) + '.png', 'rb') as f1:
                background_bytes = f1.read()
            res = det.slide_match(target_bytes, background_bytes, simple_target=False)
            print(res)
            target = res.get('target')[0]

            # 等待滑块元素可见
            slider_element = WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.tc-slider-normal')))

            # canvas_x_offset = driver.execute_script(
            #     "return window.screenX + (window.outerWidth - window.innerWidth) / 2 - window.scrollX;")
            # # Assume all the browser chrome is on the top of the screen and none on the bottom.
            # canvas_y_offset = driver.execute_script(
            #     "return window.screenY + (window.outerHeight - window.innerHeight) - window.scrollY;")
            # # Get the element center.
            # element_location = (puzzle.rect["x"] + canvas_x_offset + puzzle.rect["width"] / 2,
            #                     puzzle.rect["y"] + canvas_y_offset + puzzle.rect["height"] / 2)
            #
            # # 计算元素的中心点位置
            # x = element_location[0] + target
            # y = element_location[1]

            location = puzzle.location
            size = puzzle.size
            # 计算元素的中心点位置
            x = location['x'] + size['width'] / 2 + target
            y = location['y'] + size['height'] / 2

            # 鼠标悬停在滑块元素上
            ActionChains(driver).move_to_element(slider_element).perform()

            # 鼠标按下左键
            ActionChains(driver).click_and_hold(slider_element).perform()

            # 等待500毫秒
            time.sleep(1)

            # 鼠标移动到目标位置
            ActionChains(driver).move_by_offset(x, y).perform()

            # 等待500毫秒
            time.sleep(1)

            # 鼠标释放左键
            ActionChains(driver).release().perform()

            # 等待1.5秒
            time.sleep(1)

            try:
                # 查找验证成功的元素
                elements_3 = driver.find_element(By.CSS_SELECTOR, '.tc-success')
                if elements_3.is_displayed():
                    # 验证成功，返回
                    return
                else:
                    reload_button = driver.find_element(By.CSS_SELECTOR, '#reload')
                    reload_button.click()
            except Exception as e:
                # 如果验证不成功，则点击刷新按钮
                reload_button = driver.find_element(By.CSS_SELECTOR, '#reload')
                reload_button.click()
                driver.switch_to.default_content()

    except Exception as e:
        print(e)
        print("solve captcha failed")
        driver.switch_to.default_content()
        return


def main(num_list):
    chrome_options = Options()
    chrome_driver = CHROMEDRIVER_PATH
    chrome_options.executable_path = chrome_driver
    driver = webdriver.Chrome(options=chrome_options)

    for index, llist in enumerate(num_list):
        country_code, num = llist
        print(country_code, num)
        driver.get('http://y.tencentmusic.com/#/home')

        login_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="unlogin-box"]//a[@class="btn_start_enter2 login"]')))
        if not login_button:
            solve_captcha(driver, index)
        login_button.click()
        time.sleep(1)

        solve_captcha(driver, index)
        phone_tab = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'tab-phone')))
        if not phone_tab:
            login_button.click()
            solve_captcha(driver, index)
        phone_tab.click()
        time.sleep(1)

        country_input = driver.find_element(By.CSS_SELECTOR, '.el-select .el-input > input')
        if not country_input:
            solve_captcha(driver, index)
        # country_input.clear()
        country_input.send_keys('+' + country_code)
        country_input.send_keys(Keys.ARROW_UP)
        country_input.send_keys(Keys.RETURN)
        time.sleep(2)

        phone_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="请输入注册的手机号"]')
        # phone_input.clear()
        if not phone_input:
            solve_captcha(driver, index)
        phone_input.send_keys(num)

        send_sms_button = driver.find_element(By.XPATH, '//span[text()="发送验证码"]')
        if not send_sms_button:
            solve_captcha(driver, index)
        send_sms_button.click()

        solve_captcha(driver, index)
        time.sleep(20)

    # driver.quit()


if __name__ == '__main__':
    pwd = os.path.dirname(__file__)
    csv_file = os.path.join(pwd, "numbers.csv")
    df = pd.read_csv(csv_file, header=None)

    num_list = []
    for index, row in df[:2].iterrows():
        # 如果需要访问特定列的值，可以通过列名或索引来获取
        # 例如，获取第一列的值
        country_code, num = row[0].split("-")
        num_list.append([country_code, num])
    main(num_list)
