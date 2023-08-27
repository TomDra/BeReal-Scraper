#import keyboard
import io
import os
import pytesseract as pt
import pyautogui as pyautogui
from PIL import ImageGrab, Image
import time
import re
from pywinauto import keyboard as key
from win32gui import FindWindow, GetWindowRect
import win32api, win32con

#time.sleep(3)

def click():
    pyautogui.mouseDown(button='left')
    pyautogui.mouseUp(button='left')
    time.sleep(0.5)

def click_and_drag(x_y1,x_y2, time=0.1):
    x1,y1 = x_y1
    x2, y2 = x_y2
    pyautogui.moveTo(x1, y1)
    pyautogui.mouseDown(button='left')
    pyautogui.moveTo(x2, y2, time)
    pyautogui.mouseUp(button='left')
    #time.sleep(10)


def move_mini_pic_right():
    # Move the mini pic from the left and right
    window_handle = FindWindow(None, "LDPlayer")
    window_rect = GetWindowRect(window_handle)

    intialX=window_rect[0]
    initalY=window_rect[1]
    height = window_rect[2]
    width = window_rect[3]

    y1=int(initalY+height/4)
    x1=int(intialX+width/8)
    y2 = y1
    x2= int((intialX+(width*4/10)))

    click_and_drag([x1,y1],[x2,y2])

def swipe_previous_post():
    # Move the mini pic from the left and right
    window_handle = FindWindow(None, "LDPlayer")
    window_rect = GetWindowRect(window_handle)

    intialX = window_rect[0]
    initalY = window_rect[1]
    height = window_rect[2]
    width = window_rect[3]

    y1 = int(initalY + height / 2)
    x1 = int(intialX + width / 10)
    y2 = y1
    x2 = int((intialX + (width * 4 / 10)))

    click_and_drag([x1, y1], [x2, y2], 0.1)

def move_mini_pic_left():
    # Move the mini pic from the left and right
    window_handle = FindWindow(None, "LDPlayer")
    window_rect   = GetWindowRect(window_handle)

    intialX=window_rect[0]
    initalY=window_rect[1]
    height = window_rect[2]
    width = window_rect[3]

    y1=int(initalY+height/4)
    x1=int(intialX+width/8)
    y2 = y1
    x2= int((intialX+(width*4/10)))

    click_and_drag([x2,y2],[x1,y1])


def cut_borders(img):
    width, height = img.size

    left = 5
    bottom = height - (height/6)
    right = width-(width/15)-5
    top = height / 8-5

    # Cropped image of above dimension
    # (It will not change original image)
    result = img.crop((left, top, right, bottom))
    return result

def get_sides(img, is_left):
    width, height = img.size

    left = 0 if is_left else width/2
    bottom = height
    right = left + width/2
    top = 0

    result = img.crop((left, top, right, bottom))
    return result

def get_left(img):
    width, height = img.size

    left = 0
    bottom = height
    right = width/2
    top = 0

    result = img.crop((left, top, right, bottom))
    return result


def get_right(img):
    width, height = img.size

    left = width/2
    bottom = height
    right = width
    top = 0

    result = img.crop((left, top, right, bottom))
    return result


def combine_sides(left, right):
    image1_size = left.size
    image2_size = right.size
    new_image = Image.new('RGB', (2 * image1_size[0], image1_size[1]), (250, 250, 250))
    new_image.paste(left, (0, 0))
    new_image.paste(right, (image1_size[0], 0))
    return new_image

def first_side():
    key.send_keys("%{PRTSC}")
    img1 = ImageGrab.grabclipboard()
    date = get_date(img1)
    clear_right = cut_borders(img1)
    right = get_right(clear_right)
    move_mini_pic_right()
    key.send_keys("%{PRTSC}")
    img2 = ImageGrab.grabclipboard()
    clear_left = cut_borders(img2)
    left = get_left(clear_left)
    move_mini_pic_left()
    return combine_sides(left, right), date

def second_side():
    click()
    key.send_keys("%{PRTSC}")
    img1 = ImageGrab.grabclipboard()
    clear_right = cut_borders(img1)
    right = get_right(clear_right)
    move_mini_pic_right()
    key.send_keys("%{PRTSC}")
    img2 = ImageGrab.grabclipboard()
    clear_left = cut_borders(img2)
    left = get_left(clear_left)
    move_mini_pic_left()
    return combine_sides(left, right)



def check_and_create_directory(directory):
    """if directory not exist, create it"""
    if not os.path.exists(directory):
        os.mkdir(directory)


def convertImageFormat(imgObj, outputFormat="PNG"):
    newImgObj = imgObj
    if outputFormat and (imgObj.format != outputFormat):
        imageBytesIO = io.BytesIO()
        imgObj.save(imageBytesIO, outputFormat)
        newImgObj = Image.open(imageBytesIO)
    return newImgObj

def get_date(img):
    pt.pytesseract.tesseract_cmd = "ignore-tesseract/tesseract.exe"
    text = pt.image_to_string(convertImageFormat(img))
    print(text)
    date = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) \d+,\s?\d{4}", text)
    if date:
        print(date.group())
        return date.group()
    else:
        print('error')
        return "ERROR"

def get_images():
    time.sleep(1)
    img1, date = first_side()
    img2 = second_side()
    swipe_previous_post()
    return [img1, img2, date]

def save_image(img, name, directory):
    check_and_create_directory("images")
    checked_name = make_valid_name(name, directory)
    print("Saving "+name+".jpg")
    img.save(directory+checked_name+".jpg")

def make_valid_name(name, directory):
    if os.path.isfile(directory+name+".jpg"):
        if "}" in name:
            temp = name.split("}")
            if temp != None:
                num = temp[0]
                num = num.replace("{","")
                num = int(num)+1
                name = name.split("} ")[1]
        else:
            num = 1
        new_name = "{"+str(num)+"} "+name
        new_name = make_valid_name(new_name, directory)
        return new_name
    else:
        return name


def main(directory):
    imgs = get_images()
    save_image(imgs[0], imgs[2]+" - [1]", directory)
    save_image(imgs[1], imgs[2]+" - [2]", directory)


pyautogui.keyDown("win")
pyautogui.keyDown("1")
pyautogui.keyUp("win")
pyautogui.keyUp("1")

directory = "images/"

for i in range(100):
    main(directory)