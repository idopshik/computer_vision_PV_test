import pyautogui

# Сделайте скриншот нужной части окна и сохраните как image.png
# Затем ищите это изображение на экране

try:
    # Поиск изображения на экране
    location = pyautogui.locateOnScreen('image.png', confidence=0.8)

    if location:
        print(f"coords: {location}")
        print(f"left upper corner: ({location.left}, {location.top})")
        print(f"center: ({location.left + location.width//2}, {location.top + location.height//2})")
    else:
        print("can't find")

except pyautogui.ImageNotFoundException:
    print("can't find on the screen")
