
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


# Задайте координаты окна Vysor
monitor = {'left': 1504, 'top': 727, 'width': 290, 'height': 249}





def new_screenshot():
    """Функция для создания скриншота"""
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
        _, binary_frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)

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




        Если нажать 'q', окно закроется
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()

            if key == 's':
                new_screenshot()
            elif key == 'q':
                print("Выход...")
                break

cv2.destroyAllWindows()


