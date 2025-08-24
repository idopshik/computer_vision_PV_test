
import pyautogui

import json

import keyboard
from PIL import ImageGrab
import datetime
import os

import cv2
import mss
import numpy as np
import pytesseract
from PIL import Image
import msvcrt  # Только для Windows

from console_debug_colors import *


LOCATION_FILE = "screen_location.txt"


# Задайте координаты окна Vysor
monitor = {'left': 1492, 'top': 729, 'width': 238, 'height': 87}



def write_strings_to_json(location, filename='screen_location.json'):
    """
    Записывает переменные в JSON файл
    """
    data = {
        'left': str(location.left),
        'top': str(location.top),
        'width': str(location.width),
        'height': str(location.height)
    }

    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f" written in JSON: {filename}")
        return True
    except Exception as e:

        print(f" can't write JSON {e}")
        return False

def read_strings_from_json(filename='screen_location.json'):
    """
    Читает переменные из JSON файла
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data_str = json.load(file)
            print(data_str)
            data  = {key: int(value) for key, value in data_str.items()}
            print(type(data))
            print(data)
            return data


        #  return (data['variable1'], data['variable2'],
                #  data['variable3'], data['variable4'])

        #  except FileNotFoundError:
            #  print("can't find a file")
    except Exception as e:
        print("falt")
        #  print(f"{RED}✗ can't read JSON somehow (maybe corrupted): {e}{NC}")
        return None





def show_help():
    """Показать красивую справку"""
    help_text = """
     КОМАНДЫ СКРИНШОТТЕРА:
    ┌───────────────────────────────────────┐
    │  s    - load new screenghot           │
    │  h    - Показать справку              │
    │  q    - Выйти из программы            │
    └───────────────────────────────────────┘
     Подсказка: Приложение работает в фоне!
    """
    print(help_text)

def new_screenshot():
    # скриншот нужной части окна и сохраните как image.png
    # Затем ищите это изображение на экране
    print("\nstart searching ... \n")

    try:
        # Поиск изображения на экране
        location = pyautogui.locateOnScreen('image.png', confidence=0.8)

        if location:
            print(f"coords: {location}")
            print(f"left upper corner: ({location.left}, {location.top})")
            print(f"center: ({location.left + location.width//2}, {location.top + location.height//2})")
            print(type(location.left))

            write_strings_to_json(location)
            try:
                with open("screen_location.txt", mode="w", encoding="utf-8") as f:
                    f.writelines([str(location.left), str(location.top), str(location.width), str(location.height)])
                    pass
            except Exception as e:
                pass

            print(f"{GREEN}\nSucessfully found screen_place!\n{NC}")
        else:
            print(f"{RED}can't find{NC}")

    except pyautogui.ImageNotFoundException:
        print(f"{RED}can't find on the screen{NC}")

def make_new_screenshot():
    """только для мебели, не испльзуетс"""
    # Создаем папку для скриншотов, если её нет
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    # Генерируем имя файла с текущим временем
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'screenshots/screenshot_{timestamp}.png'

    # Делаем скриншот
    screenshot = ImageGrab.grab()
    screenshot.save(filename)
    print(f'Скриншот сохранен как: {filename}')


def main():


    monitor = read_strings_from_json()
    if monitor:
        print(f"{GREEN} loaded from JSON:{NC}", monitor)
    else:
        monitor = manual_location
        print(f"{RED}took default manually imputed values{NC}")

    # Pytesseract требует указать путь к исполняемому файлу, если он не в системных переменных
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Настройки для Pytesseract, чтобы распознавать только цифры
    # `--psm 6` - Page Segmentation Mode: распознавать как единый блок текста (single block of text)
    # `-c tessedit_char_whitelist=0123456789` - Whitelist (белый список) символов, только цифры
    custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789'


    with mss.mss() as sct:
        while True:
            sct_img = sct.grab(monitor)

            # Преобразование изображения в массив NumPy
            frame = np.array(sct_img)

            # Конвертация в оттенки серого, что обычно улучшает распознавание
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Бинаризация (черно-белое) изображение для улучшения контраста
            # Здесь 128 - пороговое значение. Вам может понадобиться его изменить
            # в зависимости от освещения и контраста вашего индикатора.
            # Например:
            # _, binary_frame = cv2.threshold(gray_frame, 150, 255, cv2.THRESH_BINARY)



            # Бинаризация: цифры БЕЛЫЕ на ЧЁРНОМ фоне
            _, thresh = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)
            # ВНИМАНИЕ: Здесь я поменял на cv2.THRESH_BINARY (не INV)

            # --- Шаг 1: Морфологическая дилатация ---
            # Создаем ядро для дилатации.
            kernel = np.ones((5,5), np.uint8)
            # Применяем дилатацию, чтобы соединить сегменты
            dilated_thresh = cv2.dilate(thresh, kernel, iterations=1)


            #  _, binary_frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)
            binary_frame = dilated_thresh

            # Передача кадра в Pytesseract для распознавания
            # Преобразуем массив NumPy обратно в объект PIL, как того требует Pytesseract
            img_pil = Image.fromarray(binary_frame)

            # Распознавание текста с использованием кастомных настроек
            # `strip()` - удаляет лишние пробелы и символы переноса строки в начале и конце
            text = pytesseract.image_to_string(img_pil, config=custom_config).strip()

            # Вывод распознанного текста в консоль, если он не пустой
            if text:
                print("num recognition:", text)

            # Для отладки: отображение обработанного кадра
            cv2.imshow('Processed Frame', binary_frame)

            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                print(key)

                if key == 's':
                    new_screenshot()
                elif key == 'h':
                    show_help()
                elif key == 'q':
                    print("Выход...")
                    break

            # Если нажать 'q', окно закроется
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("exit by second condition")
                break

    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()
    #  main()
