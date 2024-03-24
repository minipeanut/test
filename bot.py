# coding:utf-8
import ddddocr

import asyncio
import time

import requests
from pyppeteer.launcher import DEFAULT_ARGS

# DEFAULT_ARGS.remove("--enable-automation")
from pyppeteer import launch
import os

import pandas as pd


async def main(num_list):
    print("1", num_list)

    browser = await launch(headless=False)

    page = await browser.newPage()

    await page.setExtraHTTPHeaders({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        'Sec-Ch-Ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': 'Windows'
    })
    await page.goto('http://y.tencentmusic.com/#/home')
    #
    for llist in num_list:
        country_code = llist[0]
        num = llist[1]
        print(country_code, num)
        # 在当前浏览器中新建一个标签页
        new_page = await browser.newPage()
        await asyncio.sleep(1)
        # 获取所有标签页
        pages = await browser.pages()

        # 切换到新建的标签页
        await new_page.bringToFront()
        # 设置网页 视图大小
        #await new_page.setViewport(viewport={'width': 800, 'height': 600})
        await new_page.goto('http://y.tencentmusic.com/#/home')
        await asyncio.sleep(2)
        login_button = await new_page.waitForXPath('//div[@class="unlogin-box"]//a[@class="btn_start_enter2 login"]')  # 等待元素加载

        await login_button.click()
        await asyncio.sleep(1)

        # await page.xpath('//div[@id="tab-phone"]').click()
        # botton1 = await page.xpath('//div[@class="tab-item tab-item-1"]')  # 滑块拼图验证按钮
        # await botton1[0].click()
        await new_page.click('#tab-phone', options={
            'button': 'left',
            'clickCount': 1,
            'delay': 300,  # 延迟点击(ms)
        })

        # el-input el-input--suffix is-focus

        select_button = await new_page.waitForXPath('//div[@class="el-input el-input--suffix is-focus"]//span[@class="el-input__suffix"]')
        await select_button.click()
        time.sleep(0.5)

        country_dom = await new_page.waitForXPath(f'//li[@class="el-select-dropdown__item"]//span[text()="+{country_code}"]')
        await country_dom.click()
        time.sleep(0.5)

        input_element = await new_page.querySelector('input[placeholder="请输入注册的手机号"]')
        # 输入数据到输入框
        # await input_element.type(num)

        send_sms_button = await new_page.waitForXPath(f'//div[@class="phone-valicode"]//span[text()="发送验证码"]')
        await send_sms_button.click()



    # botton2 = await page.xpath('//*[@aria-label="点击按钮开始验证"]')  # 开始验证按钮
    # await botton2[0].click()
    # while True:
    #     time.sleep(5)
    #     elements_1 = await page.xpath(
    #         '//*[@id="captcha"]/div[2]/div[1]/div[4]/div[1]/div[2]/div/div/div[1]/div[1]/div[1]/@style')  # 滑块图片链接
    #     elements_2 = await page.xpath(
    #         '//*[@id="captcha"]/div[2]/div[1]/div[4]/div[1]/div[2]/div/div/div[1]/div[2]/@style')  # 背景图片链接
    #     for element in elements_1:
    #         sc = await page.evaluate('(element) => element.textContent', element)
    #         sc_url = sc.split('"')[1].split('"')[0]  # 提取滑块图片链接
    #         with open('slice.png', 'wb') as f1:
    #             f1.write(requests.get(sc_url).content)
    #     for element in elements_2:
    #         bg = await page.evaluate('(element) => element.textContent', element)
    #         bg_url = bg.split('"')[1].split('"')[0]  # 提取背景图片链接
    #         with open('bg.png', 'wb') as f2:
    #             f2.write(requests.get(bg_url).content)
    #     target = await get_xy()  # 得到滑块x坐标偏移量
    #     if target:
    #         # print(target)
    #         botton3 = await page.xpath(
    #             '//*[@id="captcha"]/div[2]/div[1]/div[4]/div[1]/div[2]/div/div/div[2]/div/div[3]')
    #         await botton3[0].hover()  # 鼠标悬停元素上
    #         await page.mouse.down()  # 鼠标落下
    #         await page.waitFor(500)
    #         x = 1116 + target
    #         y = 641
    #         await page.mouse.move(x, y, {'steps': 2})  # 鼠标移动
    #         await page.waitFor(500)
    #         await page.mouse.up()  # 鼠标松开
    #         time.sleep(2)
    #         elements_3 = await page.xpath('//*[@id="captcha"]/div[2]/div[1]/div[3]/div[2]/div/div[2]/text()')
    #         msg = ''
    #         for element in elements_3:
    #             msg = await page.evaluate('(element) => element.textContent', element)
    #         if msg == '验证通过':
    #             break
    #         else:
    #             print(msg)
    #     else:  # 获取坐标失败时刷新验证
    #         botton4 = await page.xpath('//*[@aria-label="刷新验证"]')
    #         await botton4[0].click()
    # input('---验证通过---')
    # await browser.close()


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
    for index, row in df.iterrows():
        # 如果需要访问特定列的值，可以通过列名或索引来获取
        # 例如，获取第一列的值
        country_code, num = row[0].split("-")
        num_list.append([country_code, num])

    asyncio.get_event_loop().run_until_complete(main(num_list))