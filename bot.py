# coding:utf-8

import ddddocr

import asyncio
import time

import requests
# from pyppeteer.launcher import DEFAULT_ARGS
#
# DEFAULT_ARGS.remove("--enable-automation")
from pyppeteer import launch
import os

import pandas as pd

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    'Sec-Ch-Ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': 'Windows'
}


async def solve_captcha(page, idx):
    # captcha_dom = await page.xpath('//div[@class="tc-captcha tc-drag"]')

    is_visible = await page.xpath('//*[@id="tcaptcha_transform_dy"]')
    if is_visible:
        for frame in page.frames:
            print(frame)
        #     # 切换到指定的iframe
        #     await page.goto(frame.url)
        #     print(f"已切换到iframe：{frame.url}")
        #     break

        # todo
        elements_1 = await page.xpath('//div[@id="tcOperation"]/div[@class="tc-fg-item"]/@style')  # 滑块图片链接

        element_position = {}

        elements_2 = await page.xpath('//div[@id="slideBgWrap"]/div/@style')  # 背景图片链接
        for frame in page.frames:
            print(frame)
        img_size = 0
        index = 0
        for element in elements_1:
            sc = await page.evaluate('(element) => element.textContent', element)
            sc_url = sc.split('"')[1].split('"')[0]  # 提取滑块图片链接
            print(sc_url)
            with open('slice' + str(idx) + '.png', 'wb') as f1:
                if len(requests.get(sc_url).content) > img_size:

                    # todo
                    element_position = await page.evaluate('''() => {
                        const element = document.querySelector('#tcOperation > .tc-fg-item');
                        const rect = element.getBoundingClientRect();
                        
                        // 获取页面的滚动偏移量
                        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
                        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                        
                        // 计算元素相对于屏幕的坐标
                        const x = rect.left + scrollLeft;
                        const y = rect.top + scrollTop;

                        return {
                            x: rect.x + rect.width / 2,
                            y: rect.y + rect.height / 2
                        };
                    }''')

                    print(element_position)
                    img_size = len(requests.get(sc_url).content)
                    f1.write(requests.get(sc_url).content)
            index += 1
        for element in elements_2:
            bg = await page.evaluate('(element) => element.textContent', element)
            bg_url = bg.split('"')[1].split('"')[0]  # 提取背景图片链接
            print(bg_url)
            with open('bg.png' + str(idx) + 'wb') as f2:
                f2.write(requests.get(bg_url).content)
        target = await get_xy()  # 得到滑块x坐标偏移量
        if target:
            # print(target)
            botton3 = await page.xpath('//div[@class="tc-fg-item tc-slider-normal"]')
            await botton3[0].hover()  # 鼠标悬停元素上
            await page.mouse.down()  # 鼠标落下
            await page.waitFor(500)
            x = element_position.x + target
            y = element_position.y
            await page.mouse.move(x, y, {'steps': 2})  # 鼠标移动
            await page.waitFor(500)
            await page.mouse.up()  # 鼠标松开
            await asyncio.sleep(1.5)
            elements_3 = await page.xpath('//div[@id="tcOperation"]/div[@class="tc-cover tc-success"]')
            if elements_3[0].isIntersectingViewport():
                return
            else:
                reload_botton = await page.xpath('//div[@id="reload"]')
                await reload_botton[0].click()
        else:  # 获取坐标失败时刷新验证
            reload_botton = await page.xpath('//div[@id="reload"]')
            await reload_botton[0].click()

async def main(num_list):

    browser = await launch(headless=False, defaultViewport={'width': 1500, 'height': 800}, args=['--start-maximized'])

    for index, llist in enumerate(num_list):
        country_code, num = llist
        print(country_code, num)
        # 在当前浏览器中新建一个标签页
        new_page = await browser.newPage()
        await asyncio.sleep(1)

        # 切换到新建的标签页
        await new_page.bringToFront()
        await new_page.setExtraHTTPHeaders(header)
        # 设置网页 视图大小
        #await new_page.setViewport(viewport={'width': 800, 'height': 600})
        await new_page.goto('http://y.tencentmusic.com/#/home')

        await asyncio.sleep(2)
        login_button = await new_page.xpath('//div[@class="unlogin-box"]//a[@class="btn_start_enter2 login"]')  # 等待元素加载
        if not login_button:
            await solve_captcha(new_page, index)
        await login_button[0].click()
        await asyncio.sleep(2)

        await solve_captcha(new_page, index)
        await new_page.click('#tab-phone', options={
            'button': 'left',
            'clickCount': 1,
            'delay': 300,  # 延迟点击(ms)
        })
        await solve_captcha(new_page, index)
        # el-input el-input--suffix is-focus
        country_dom = await new_page.querySelector('.el-select .el-input')
        if not country_dom:
            await solve_captcha(new_page, index)

        await country_dom.click()
        await asyncio.sleep(0.5)
        await solve_captcha(new_page, index)

        country_dom = await new_page.querySelector('.el-select .el-input > input')
        if not country_dom:
            await solve_captcha(new_page, index)
        await country_dom.type('+' + country_code)
        await new_page.keyboard.press('ArrowUp')  # 按下上键
        await new_page.keyboard.press('Enter')  # 按下回车键
        await solve_captcha(new_page, index)
        await asyncio.sleep(0.5)

        input_element = await new_page.querySelector('input[placeholder="请输入注册的手机号"]')
        if not input_element:
            await solve_captcha(new_page, index)

        await asyncio.sleep(0.5)
        await input_element.type(num)
        await solve_captcha(new_page, index)

        send_sms_button = await new_page.waitForXPath(f'//span[text()="发送验证码"]')
        if not send_sms_button:
            await solve_captcha(new_page, index)
        await asyncio.sleep(1)
        # await send_sms_button.click()


async def get_xy():
    det = ddddocr.DdddOcr(det=False, ocr=False)

    with open('slice.png', 'rb') as f:
        target_bytes = f.read()

    with open('bg.png', 'rb') as f:
        background_bytes = f.read()
    try:
        res = det.slide_match(target_bytes, background_bytes)
        print(res)
        return res.get('target')[0]
    except:
        return False


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

    asyncio.get_event_loop().run_until_complete(main(num_list))