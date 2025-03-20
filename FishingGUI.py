import time
import cv2
import pyautogui
import pydirectinput  # Direct input for better keypress reliability
import numpy as np
import win32gui, win32ui, win32con
import tkinter as tk
from tkinter import messagebox, scrolledtext
from ultralytics import YOLO  # Import YOLOv8 model
import threading
import os
import ctypes
import sys

# 检查是否以管理员权限运行
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 如果没有管理员权限，则重新运行自己，并申请权限
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# Define model path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取程序的运行目录（支持 .exe 和 .py 运行）
if getattr(sys, 'frozen', False):  # 检测是否在 PyInstaller 生成的 .exe 运行
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")

# 确保 `models` 目录存在，并且 `best.pt` 没有被打包进 .exe
if not os.path.exists(MODEL_PATH):
    print("❌ YOLO model not found! Please place `best.pt` in the `models` folder.")
    sys.exit(1)

print(f"🔍 Loading YOLO model from: {MODEL_PATH}")
model = YOLO(MODEL_PATH)

# Game window title
GAME_WINDOW = "天涯明月刀"

running = False  # Global variable to control the bot execution

# Function to capture only the game window
def capture_game_window(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd == 0:
        log_message("❌ Game window not found!")
        return None

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    hwindc = win32gui.GetWindowDC(hwnd)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (0, 0), win32con.SRCCOPY)

    bmp_info = bmp.GetInfo()
    bmp_str = bmp.GetBitmapBits(True)
    img = np.frombuffer(bmp_str, dtype=np.uint8)
    img.shape = (bmp_info['bmHeight'], bmp_info['bmWidth'], 4)

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

# Function to check what YOLO detects in the game window
def detect_fishing_state():
    frame = capture_game_window(GAME_WINDOW)
    if frame is None:
        return None

    results = model(frame)
    detected_classes = [model.names[int(box.cls)] for result in results for box in result.boxes]
    return detected_classes

# Function to log messages in the GUI
def log_message(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)

# Fishing Bot Algorithm
def start_fishing_bot():
    global running
    running = True
    log_message("🎣 Bot will start in 10 seconds. Switch to the game window...")
    time.sleep(10)

    while running:
        if not running:
            break
        pyautogui.click()
        time.sleep(0.5)
        pydirectinput.press("f1")
        log_message("🎣 Pressing F1 to start fishing...")

        start_time = time.time()
        fish_on_hook_count = 0
        while running:
            if time.time() - start_time > 25:
                log_message("⏳ No fish detected after 25 seconds! Restarting fishing...")
                return start_fishing_bot()
            detected = detect_fishing_state()
            if detected and "Fish_OnHook" in detected:
                fish_on_hook_count += 1
                log_message(f"🐟 Fish_OnHook detected {fish_on_hook_count} times.")
                if fish_on_hook_count >= 2:
                    time.sleep(0.3)
                    pyautogui.click()
                    pydirectinput.press("f")
                    log_message("✅ Reeling in fish!")
                    break
            time.sleep(0.2)
        start_time = time.time()
        while running:
            if time.time() - start_time > 16:
                log_message("⏳ No fish detected after 16 seconds! Restarting fishing...")
                return start_fishing_bot()
            detected = detect_fishing_state()
            if detected and "Perfect_Time" in detected:
                log_message("🎯 Perfect timing detected! Pressing 'F'.")
                pydirectinput.press("f")
                break
            time.sleep(0.2)

        log_message("⏳ Waiting 5 seconds before restarting fishing...")
        time.sleep(5)

# Stop function
def stop_fishing_bot():
    global running
    running = False
    log_message("🛑 Stopping bot!")

# GUI Setup
root = tk.Tk()
root.title("Fishing Bot")
root.geometry("400x300")

start_button = tk.Button(root, text="Start Fishing Bot", command=lambda: threading.Thread(target=start_fishing_bot, daemon=True).start())
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop Fishing Bot", command=stop_fishing_bot)
stop_button.pack(pady=5)

log_text = scrolledtext.ScrolledText(root, height=10, width=50)
log_text.pack(pady=5)

def show_about():
    messagebox.showinfo("About", "🔹 **使用说明**\n\n"
                        "✅ **快捷键设置**\n"
                        "- 默认 F1 为钓鱼快捷键。\n\n"
                        "✅ **游戏设置**\n"
                        "- 请确保钓鱼武学绑定到快捷键 (F1 默认)。\n"
                        "- **指向性技能施放方式** 必须改为 **快速智能施放**。\n\n"
                        "✅ **程序运行方式**\n"
                        "- 点击 **开始** 按钮后，需手动切换到游戏，程序会等待 **10秒**。\n"
                        "- **自动识别鱼上钩** (Fish_OnHook) 并按 F 键收杆。\n"
                        "- **自动识别完美时机** (Perfect_Time) 并快速按 F 键两次。\n"
                        "- **ESC 键可随时停止程序。")

about_button = tk.Button(root, text="About", command=show_about)
about_button.pack(pady=5)

root.mainloop()
