import time
import cv2
import pyautogui
import pydirectinput  # Direct input for better keypress reliability
import keyboard
import numpy as np
import win32gui, win32ui, win32con
from ultralytics import YOLO  # Import YOLOv8 model
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

    print(f"📸 Capturing game window ({width}x{height}) at position ({left},{top})")

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

    print("✅ Game window captured successfully.")
    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

# Function to check what YOLO detects in the game window
def detect_fishing_state():
    print("🔍 Capturing game window for YOLO detection...")
    frame = capture_game_window(GAME_WINDOW)
    if frame is None:
        print("❌ Failed to capture game window! Retrying...")
        return None

    print("🤖 Running YOLO model on the captured frame...")
    results = model(frame)
    detected_classes = [model.names[int(box.cls)] for result in results for box in result.boxes]

    if detected_classes:
        print(f"🎯 YOLO detected: {detected_classes}")
    else:
        print("🚫 YOLO detected nothing.")

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
            # ⏳ Check if 25 seconds passed before detecting anything
            if time.time() - start_time > 26:
                print("⏳ No confirmed fish detected after 25 seconds! Restarting fishing...")
                return start_fishing_bot(first_run=False, delay_f1=True)  # 🔄 Restart with 2s delay

            detected = detect_fishing_state()
            if detected is None:
                continue

            if "Fish_OnHook" in detected:
                fish_on_hook_count += 1
                print(f"🐟 Fish_OnHook detected {fish_on_hook_count} times.")

                if fish_on_hook_count >= 2:  # Confirm detection before proceeding
                    print("✅ Confirmed Fish_OnHook! Reeling in fish...")
                    time.sleep(0.5)

                    print("🖱️ Clicking on the game to ensure focus...")
                    pyautogui.click()

                    print("🎣 Pressing 'F' to reel in the fish...")
                    time.sleep(0.2)
                    pydirectinput.press("f")
                    print("✅ Pressed 'F' successfully!")
                    break  # Move to next stage

            else:
                fish_on_hook_count = 0  # Reset counter if Fish_OnHook is missing

            time.sleep(0.2)  # Wait before next detection

        # Detect "Perfect_Time"
        while True:
                        # ⏳ Check if 16 seconds passed before detecting anything
            if time.time() - start_time > 16:
                print("⏳ No confirmed Perfect_Time detected after 16 seconds! Restarting fishing...")
                return start_fishing_bot(first_run=False, delay_f1=True)  # 🔄 Restart with 2s delay
            
            detected = detect_fishing_state()
            if detected is None:
                continue

            if "Fish_OnHook" in detected:  # If Fish_OnHook appears again, go back to previous stage
                print("🔄 Fish_OnHook appeared again! Returning to previous detection.")
                return start_fishing_bot(first_run=False, delay_f1=False)

            if "Perfect_Time" in detected:
                print("🎯 Perfect timing detected! Pressing 'F' in 0.5s...")
                pydirectinput.press("f")               
                print("✅ Pressed 'F' for perfect timing!")
                break

        # **After fishing, wait only 8 seconds before restarting**
        print("⏳ Waiting 5 seconds before restarting fishing...")
        time.sleep(5)
        return start_fishing_bot(first_run=False, delay_f1=False)  # 🔄 Restart fishing (without extra delay)

# Run the bot
start_fishing_bot(first_run=True, delay_f1=False)
