# Fishing Bot

Fishing Bot is an automated fishing tool for the game **天涯明月刀**. It uses YOLOv8 to detect fishing states and automatically reel in fish at the perfect timing. The bot runs with a GUI and provides real-time logging of fishing activity.

## 🚀 Features

- **Automated Fishing**: Presses F1 to start fishing, detects when a fish is on the hook, and reels it in automatically.
- **Perfect Timing Detection**: Identifies the perfect timing to reel in the fish and presses 'F'.
- **Logging and GUI**: Real-time logging of fishing actions with a graphical user interface.
- **Admin Privilege Handling**: Automatically requests admin privileges on startup.
- **Custom Model Support**: Uses YOLOv8 model placed in the `models` folder.

## 📝 Prerequisites

- **Python 3.9+**
- **Windows OS**
- **CUDA (if using GPU)**
- **Visual Studio Code (Recommended for development)**

### 🐍 Python Dependencies

To ensure all necessary packages are installed, follow these steps:

1. Check your Python and pip versions first:
   ```bash
   python --version
   pip --version
   ```

2. Update `pip` to the latest version:
   ```bash
   pip install --upgrade pip
   ```

3. Install the required packages using the following command:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or manually install:
   ```bash
   pip install ultralytics opencv-python pyautogui pydirectinput keyboard numpy pywin32
   ```

## &#x20;Project Structure

## 📂

## 🛠 Usage
1. Clone or download the project folder.
2. Place your `best.pt` file in the `models/` folder.
3. Run the script:

4. Switch to the game window within 10 seconds.

### Running from Source Code (Python)

1. Open **VS Code** and load the project folder.
2. Open a terminal in VS Code.
3. Install dependencies using:
4. Run the script:
```bash
   python FishingGUI.py
```
## 📝 Instructions

- Make sure the **Fishing Skill** is bound to **F1**.
- Set **Directional Skill Casting Mode** to **Quick Smart Casting**.
- Press **Start** on the GUI and switch to the game window within 10 seconds.
- The bot will automatically fish and reel in the catch at the perfect timing.
- Press **Stop** on the GUI or press **ESC** to terminate the bot.

## 🐛 Troubleshooting

- If the bot is not working properly, check the following:
  - Ensure the game window title is **天涯明月刀**.
  - Check the model path (`models/best.pt`) and make sure the file exists.
  - Run the program as **Administrator**.
- For missing modules or dependency issues, run:

## 📝 License

This project is for educational and personal use only. Please comply with the game’s terms of service before using.

