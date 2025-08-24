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

def auto_rotate(img):
    h, w = img.shape[:2]
    roi = img[int(h*0.7):h, int(w*0.7):w]  # правый-низ
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    if np.mean(gray) < 200:  # если "mm" не светлое
        img = cv2.rotate(img, cv2.ROTATE_180)
    return img

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
        raise ValueError("Экран не найден!")

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

def read_number(warp):
    """Распознаём всё число на экране"""
    h, w = warp.shape[:2]
    digits = []
    # предполагаем 6 цифр, фиксированные окна
    cell_w = w // 6
    for i in range(6):
        roi = warp[30:130, i*cell_w:(i+1)*cell_w]
        d = read_digit(roi)
        digits.append(d)

    num_str = "".join(digits).replace("?", "")
    try:
        return float(num_str)/100  # поправка на десятичную точку
    except:
        return None

# --- тест ---
frame = cv2.imread("indicator.jpg")
warp = extract_screen(frame)
val = read_number(warp)
print("Распознанное значение:", val)

cv2.imshow("warp", warp)
cv2.waitKey(0)






