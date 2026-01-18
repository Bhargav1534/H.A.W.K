import pyautogui, os

class InputTools:
    def __init__(self):
        pass

    @staticmethod
    def move_mouse(x: int, y: int, duration: float = 0.5):
        pyautogui.moveTo(x, y, duration=duration)

    @staticmethod
    def click_mouse(x: int, y: int, button: str):
        pyautogui.click(x, y, button=button)

    @staticmethod
    def scroll_mouse(amount: int):
        pyautogui.scroll(amount)
    
    @staticmethod
    def get_mouse_position():
        return pyautogui.position()
    
    @staticmethod
    def drag_mouse(x: int, y: int, duration: float = 0.5, button: str = 'left'):
        pyautogui.dragTo(x, y, duration=duration, button=button) 
    
    @staticmethod
    def type_text(text: str, interval: float = 0.1):
        pyautogui.write(text, interval=interval)
    
    @staticmethod
    def press_key(key: str):
        pyautogui.press(key)

    @staticmethod
    def hotkey(*keys):
        pyautogui.hotkey(*keys)

    @staticmethod
    def screenshot(region: tuple = None):
        return pyautogui.screenshot(region=region)
    
    @staticmethod
    def alert(message: str, title: str = 'Alert'):
        pyautogui.alert(text=message, title=title)

    @staticmethod
    def confirm(message: str, title: str = 'Confirm'):
        return pyautogui.confirm(text=message, title=title)

if __name__ == "__main__":
    # os.mkdir("test_screenshots")
    os.chdir("memory")
    os.mkdir("test_screenshots")
    # InputTools.screenshot().save("test_screenshots/full_screenshot.png")