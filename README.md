Gambit

A small Windows desktop app that automatically finds a new wallpaper every day, matching a genre you choose, and sets it as your desktop background.

Features:
1) Gambit runs in background and changes your windows wallpaper.
2) It saves your previous choice of genre and changes the wallpaper according to that genre only.
3) It automatically downloads and deletes the images in 14 days so you don't have to worry about them being on your device.

How i built it:
* I used python as the core language for this.
* Wallpapers.com API for different images everyday.
* Libraries such as:
  - pyQt6
  - requests
  - ctypes
  - windows Task Scheduler


How to set it up:

Option 1: Download the app

1. Go to the "Releases" section of this repository.
2. Download the latest `Gambit.exe`.
3. Run `Gambit.exe`.
4. Choose the type of wallpapers you want.
5. Choose the folder where you want Gambit to save downloaded wallpapers.
6. Click CHANGE WALLPAPER.

Option 2: Run from source

If you want to run Gambit from the source code instead of the executable:
```bash
git clone https://github.com/vedansh201/Gambit.git
cd Gambit
pip install -r requirements.txt
python main.py
```

Requirements:
-Windows
-Internet connection
-Python 3.10+

How it works

Gambit asks the Wallpapers.com API for wallpapers matching the genre you selected. It chooses a wallpaper,
downloads it to your selected folder, and sets it as your Windows desktop wallpaper.
Gambit keeps track of previously used wallpaper IDs to reduce repeats.
It also checks the date so the wallpaper is changed only once per day.
Downloaded Gambit wallpapers older than 14 days are automatically deleted.


<img width="752" height="943" alt="image" src="https://github.com/user-attachments/assets/ec1d3134-96f8-4ea9-b8ce-12813baf33f6" />
