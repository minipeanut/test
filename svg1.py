import easygui as eg
import os
import cv2
from PIL import Image
from rembg import remove

input_path = 'received_912275164011811.jpeg'
output_path_with_alpha = 'temp_with_alpha.png'
final_output_path = 'output_white_background.png'

# 使用rembg移除背景
with open(input_path, 'rb') as i:
    input_data = i.read()
    output_data = remove(input_data, alpha_matting=True)
    with open(output_path_with_alpha, 'wb') as temp_output:
        temp_output.write(output_data)

# 打开带有透明背景的图像
img_with_alpha = Image.open(output_path_with_alpha)

# 创建一个白色背景图像
white_bg_image = Image.new("RGBA", img_with_alpha.size, "WHITE")
# 将原始图像粘贴到白色背景上，使用alpha通道作为mask
white_bg_image.paste(img_with_alpha, mask=img_with_alpha.split()[3])
white_bg_image.save(final_output_path)

from PIL import Image
import easygui as eg
import os


def analyze(img, threshold):
    if threshold < 0:
        threshold = 0
    if threshold > 100:
        threshold = 100

    width, height = img.size
    img = img.convert('L')  # 转为灰度图
    pixel = img.load()  # 获取灰度值

    for w in range(width):
        for h in range(height):
            if w == width - 1 or h == height - 1:
                continue
            xy = pixel[w, h]
            x1y1 = pixel[w + 1, h + 1]
            diff = abs(xy - x1y1)
            if diff >= threshold:
                pixel[w, h] = 60  # 灰度越大越白，代表是轮廓
            else:
                pixel[w, h] = 250  # 灰度越大越白，代表是轮廓

    return img


def main():
    threshold = 16
    pth = eg.fileopenbox(title='请打开要转换的图片')  # 打开图片
    dir = os.path.dirname(pth)  # 返回图片所在的路径
    ori_name = os.path.basename(pth)  # 返回图片名称及扩展名
    name = os.path.splitext(ori_name)[0]  # 返回图片名称
    geshi = os.path.splitext(ori_name)[1]  # 返回图片的扩展名
    out_name = os.path.join(dir, name +'(素描版)' + geshi)  # 输出的名字及路径
    img = Image.open(pth)
    img = analyze(img, threshold)
    img.save(out_name)



def main1():
    pth = eg.fileopenbox(title='请打开要转换的图片')  # 打开图片
    dir = os.path.dirname(pth)  # 返回图片所在的路径
    ori_name = os.path.basename(pth)  # 返回图片名称及扩展名
    name = os.path.splitext(ori_name)[0]  # 返回图片名称
    geshi = os.path.splitext(ori_name)[1]  # 返回图片的扩展名
    out_name = os.path.join(dir, name +'(sumiao)' + geshi)  # 输出的名字及路径
    img = cv2.imread(pth)
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, ksize=(11, 11),sigmaX=0, sigmaY=0)
    img_out=cv2.divide(img_gray, img_blur, scale=255)
    cv2.imwrite(out_name, img_out)

if __name__=='__main__':
    main1()