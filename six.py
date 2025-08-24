# GPG-5 generated code (and Grock edited)

import cv2
import numpy as np

# --- карта сегментов ---
DIGITS = {
    (1,1,1,1,1,1,0): "0",
    (0,1,1,0,0,0,0): "1",
    (1,1,0,1,1,0,1): "2",
    (1,1,1,1,0,0,1): "3",
    (0,1,1,0,0,1,1): "4",
    (1,0,1,1,0,1,1): "5",
    (1,0,1,1,1,1,1): "6",
    (1,1,1,0,0,0,0): "7",
    (1,1,1,1,1,1,1): "8",
    (1,1,1,1,0,1,1): "9",
}

# --- сегменты внутри одной цифры (относительно ROI) ---
SEGMENTS = [
    (0.2, 0.05, 0.6, 0.15),   # a
    (0.75,0.15,0.9, 0.45),    # b
    (0.75,0.55,0.9, 0.85),    # c
    (0.2, 0.85,0.6, 0.95),    # d
    (0.05,0.55,0.2, 0.85),    # e
    (0.05,0.15,0.2, 0.45),    # f
    (0.2, 0.45,0.6, 0.55),    # g
]

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

#  def orig_auto_rotate(img):
    #  h, w = img.shape[:2]
    #  roi = img[int(h*0.7):h, int(w*0.7):w]  # правый-низ
    #  gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    #  if np.mean(gray) < 200:  # если "mm" не светлое
        #  img = cv2.rotate(img, cv2.ROTATE_180)
    #  return img



def auto_rotate(img):
    h, w = img.shape[:2]
    roi = img[int(h*0.7):h, int(w*0.7):w]  # Правый-низ для проверки "mm"
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Простая проверка на "mm" (можно улучшить с помощью OCR, например Tesseract)
    template = cv2.imread("mm_template.png", 0)  # Предполагаем, что у тебя есть шаблон "mm"
    if template is None:
        raise ValueError("template not found")
    res = cv2.matchTemplate(thresh, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= 0.8)  # Порог совпадения
    if len(loc[0]) == 0:  # Если "mm" не найдено, поворачиваем
        img = cv2.rotate(img, cv2.ROTATE_180)
    return img








#gpt_5
def extract_screen(frame, dst_w=400, dst_h=160):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _,thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    contours,_ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    screen_cnt = None
    max_area = 0
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        area = cv2.contourArea(c)
        if len(approx) == 4 and area > max_area:
            screen_cnt = approx
            max_area = area

    if screen_cnt is None:
        raise ValueError("display isn't found")

    rect = order_points(screen_cnt.reshape(4,2))
    dst = np.array([[0,0],[dst_w-1,0],[dst_w-1,dst_h-1],[0,dst_h-1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warp = cv2.warpPerspective(frame, M, (dst_w, dst_h))
    return auto_rotate(warp)

def read_digit(img):
    """Распознаём одну цифру"""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    on = []
    for (x1,y1,x2,y2) in SEGMENTS:
        x1i, y1i, x2i, y2i = int(x1*w), int(y1*h), int(x2*w), int(y2*h)
        roi = binary[y1i:y2i, x1i:x2i]
        mean_val = np.mean(roi)
        on.append(1 if mean_val < 128 else 0)

    return DIGITS.get(tuple(on), "?")

#  def orig_read_number(warp):
    #  """Распознаём всё число на экране"""
    #  h, w = warp.shape[:2]
    #  digits = []
    #  # предполагаем 6 цифр, фиксированные окна
    #  cell_w = w // 6
    #  for i in range(6):
        #  roi = warp[30:130, i*cell_w:(i+1)*cell_w]
        #  d = read_digit(roi)
        #  digits.append(d)

    #  num_str = "".join(digits).replace("?", "")
    #  try:
        #  return float(num_str)/100  # поправка на десятичную точку
    #  except:
        #  return None

def read_number(warp):
    h, w = warp.shape[:2]
    gray = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, np.ones((3,3), np.uint8))

    # Проверка минуса
    minus_roi = binary[30:130, 0:int(w*0.2)]  # Левая часть для минуса
    is_negative = np.mean(minus_roi) < 128

    # Поиск контуров цифр
    contours, _ = cv2.findContours(binary[30:130], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    digits = []
    for c in contours:
        x, y, w_c, h_c = cv2.boundingRect(c)
        if w_c > 10 and h_c > 50:  # Фильтр мелких контуров
            roi = warp[30:130, x:x+w_c]
            d = read_digit(roi)
            digits.append((x, d))

    # Сортировка по x и сбор числа
    digits.sort(key=lambda x: x[0])
    num_str = "".join(d[1] for d in digits).replace("?", "")

    # Поиск десятичной точки (упрощённо, можно улучшить)
    dot_pos = num_str.find(".") if "." in num_str else -1
    if dot_pos == -1:
        try:
            val = float(num_str) / 10 if len(num_str) == 4 else float(num_str)  # Адаптивная поправка
        except:
            return None
    else:
        val = float(num_str)

    return -val if is_negative else val

# --- тест ---
#  frame = cv2.imread("images/blury_indicator.png")
#  frame = cv2.imread("images/blury_ind2.png")
#  frame = cv2.imread("images/rect.png")
#  frame = cv2.imread("images/indicator.png")
#  frame = cv2.imread("images/indicator_tilt.png")
#  warp = extract_screen(frame)
#  val = read_number(warp)
#  print("recognized_digits:", val)

#  cv2.imshow("warp", warp)
#  cv2.waitKey(0)


# Загружаем изображение
frame = cv2.imread("images/indicator_tilt.png")
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5,5), 0)
_,thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

# 1. ПОКАЖЕМ ЧЕРНО-БЕЛОЕ ИЗОБРАЖЕНИЕ ПОСЛЕ ПОРОГА
# Это самое важное для диагностики. Виден ли на нем четкий белый прямоугольник на черном фоне?
cv2.imshow('1. Threshold (Binarization)', thresh)

# 2. НАРИСУЕМ ВСЕ КОНТУРЫ, КОТОРЫЕ НАШЕЛ ALGORITHM
# Создадим копию исходного изображения для рисования
contour_image = frame.copy()
contours,_ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# Рисуем ВСЕ контуры зеленым цветом
cv2.drawContours(contour_image, contours, -1, (0,255,0), 2)
cv2.imshow('2. All Found Contours', contour_image)

# 3. ПРОЙДЕМСЯ ПО КОНТУРАМ И ПОПРОБУЕМ ИХ АППРОКСИМИРОВАТЬ
approx_image = frame.copy()
for c in contours:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    area = cv2.contourArea(c)
    # Рисуем аппроксимированный контур
    # Синий - любой контур
    cv2.drawContours(approx_image, [approx], -1, (255, 0, 0), 2)
    # Зеленый - если у него 4 угла
    if len(approx) == 4:
        cv2.drawContours(approx_image, [approx], -1, (0, 255, 0), 3)
        print(f"Found 4-point contour with area: {area}") # Выведем площадь в консоль

cv2.imshow('3. Contour Approximation (Blue: any, Green: quadrilateral)', approx_image)

cv2.waitKey(0)
cv2.destroyAllWindows()

# Только после этого пробуем запустить основную функцию
try:
    warp = extract_screen(frame)
    cv2.imshow('Result', warp)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
except ValueError as e:
    print(e)



