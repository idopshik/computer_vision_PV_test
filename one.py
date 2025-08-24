
import cv2
import mss
import numpy as np

# Задайте координаты окна Vysor
# Вы можете найти их вручную или с помощью библиотеки pyautogui
# Например: left, top, width, height
monitor = {'left': 1504, 'top': 727, 'width': 290, 'height': 249}

with mss.mss() as sct:
    while True:
        # Захват изображения с экрана
        sct_img = sct.grab(monitor)

        # Преобразование изображения в массив numpy, который понимает OpenCV
        frame = np.array(sct_img)

        # Конвертация BGR в RGB для отображения, если нужно
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Здесь вы можете обработать кадр с помощью OpenCV или Pytesseract
        # Например, вывести его на экран для проверки
        cv2.imshow('Vysor Camera Feed', frame)

        # Если нажать 'q', окно закроется
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()


