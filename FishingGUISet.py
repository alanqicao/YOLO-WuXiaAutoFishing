import time
import cv2
import pyautogui
import pydirectinput  # Direct input for better keypress reliability
import keyboard
import numpy as np
import win32gui, win32ui, win32con
import tkinter as tk
from tkinter import messagebox
from ultralytics import YOLO  # Import YOLOv8 model
import threading
import os

# Define model path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")

if not os.path.exists(MODEL_PATH):
    print(f"❌ YOLO model not found! Place 'best.pt' in 'models' folder.")
    exit(1)

print(f"🔍 Loading YOLO model from: {MODEL_PATH}")
model = YOLO(MODEL_PATH)

# Game window title
GAME_WINDOW = "天涯明月刀"

# Function to capture only the game window
def capture_game_window(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd == 0:
        print("❌ Game window not found!")
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

# Fishing Bot Algorithm
def start_fishing_bot(first_run=True, delay_f1=False):
    if first_run:
        print("🎣 Bot will start in 10 seconds. Switch to the game window...")
        time.sleep(10)  # Wait only the first time

    while True:
        if keyboard.is_pressed("esc"):
            print("🛑 Stopping bot!")
            break

        print("🖱️ Clicking to focus on the game window...")
        pyautogui.click()
        time.sleep(0.5)

        if delay_f1:
            print("⏳ Waiting 5 seconds before pressing F1...")
            time.sleep(5)

        print("🎣 Pressing F1 to start fishing...")
        pydirectinput.press("f1")

        # Detect "Fish_OnHook" (Timeout 25s)
        start_time = time.time()
        fish_on_hook_count = 0  # Counter to confirm Fish_OnHook
        while True:
            if time.time() - start_time > 25:
                print("⏳ No confirmed fish detected after 25 seconds! Restarting fishing...")
                return start_fishing_bot(first_run=False, delay_f1=True)

            detected = detect_fishing_state()
            if detected is None:
                continue

            if "Fish_OnHook" in detected:
                fish_on_hook_count += 1
                print(f"🐟 Fish_OnHook detected {fish_on_hook_count} times.")

                if fish_on_hook_count >= 2:
                    print("✅ Confirmed Fish_OnHook! Reeling in fish...")
                    time.sleep(0.5)
                    pyautogui.click()
                    pydirectinput.press("f")
                    break
            else:
                fish_on_hook_count = 0
            time.sleep(0.2)

        # Detect "Perfect_Time"
        while True:
            detected = detect_fishing_state()
            if detected is None:
                continue

            if "Perfect_Time" in detected:
                print("🎯 Perfect timing detected! Pressing 'F' in 0.5s...")
                pydirectinput.press("f")
                break

        print("⏳ Waiting 5 seconds before restarting fishing...")
        time.sleep(5)
        return start_fishing_bot(first_run=False, delay_f1=False)

# GUI Setup
root = tk.Tk()
root.title("Fishing Bot")
root.geometry("300x200")

start_button = tk.Button(root, text="Start Fishing Bot", command=lambda: threading.Thread(target=start_fishing_bot, daemon=True).start())
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Fishing Bot", command=lambda: keyboard.press("esc"))
stop_button.pack(pady=10)

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
                        "- **自动识别完美时机** (Perfect_Time) 并快速按 F 键。\n"
                        "- **ESC 键可随时停止程序。")

about_button = tk.Button(root, text="About", command=show_about)
about_button.pack(pady=10)

root.mainloop()
