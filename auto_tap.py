import pyautogui
import cv2
import numpy as np
import time
import os
import keyboard
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ================= KONFIGURASI UTAMA =================
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

running = False
mode = "click"           # Opsi: "click" atau "key"
target_key = "f"         # Tombol yang akan ditekan
key_press_count = 1      # Jumlah tekanan tombol per target
cooldown_after_key = 2.1 # JEDA (DETIK) setelah tekan tombol agar tidak spam (Ubah sesuai kebutuhan)

template_folder = "templates"
# =====================================================

templates = []
clicked_positions = []
reload_lock = False
watchdog_active = True
last_snapshot = set()
poll_interval = 3

def load_templates():
    global templates, reload_lock
    if reload_lock: return
    reload_lock = True
    try:
        templates.clear()
        if not os.path.exists(template_folder): os.makedirs(template_folder)
        print("\nReloading templates...")
        for file in os.listdir(template_folder):
            if file.endswith(".png"):
                path = os.path.join(template_folder, file)
                img = cv2.imread(path, 0)
                if img is not None:
                    templates.append((file, img))
                    print("Loaded:", file)
        print("Total Template:", len(templates))
    except Exception as e:
        print("Template load error:", e)
    reload_lock = False

class TemplateWatcher(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.src_path.endswith(".png"): load_templates()

def start_watchdog():
    global watchdog_active
    try:
        observer = Observer()
        observer.schedule(TemplateWatcher(), template_folder, recursive=False)
        observer.start()
        print("Watchdog realtime aktif ✔")
        while True: time.sleep(1)
    except:
        watchdog_active = False

def polling_watcher():
    global last_snapshot
    while True:
        if watchdog_active:
            time.sleep(2)
            continue
        try:
            current = set(os.listdir(template_folder))
            if current != last_snapshot:
                last_snapshot = current
                load_templates()
        except: pass
        time.sleep(poll_interval)

def is_close(pos, pos_list, distance=40):
    for p in pos_list:
        if abs(pos[0] - p[0]) < distance and abs(pos[1] - p[1]) < distance:
            return True
    return False

if not os.path.exists(template_folder): os.makedirs(template_folder)
load_templates()
last_snapshot = set(os.listdir(template_folder))

threading.Thread(target=start_watchdog, daemon=True).start()
threading.Thread(target=polling_watcher, daemon=True).start()

print("-" * 35)
print("HOTKEYS CONTROL:")
print("6 = PLAY")
print("7 = HOLD TO PAUSE")
print("8 = MODE KLIK MOUSE")
print("9 = MODE KEY (" + target_key.upper() + ")")
print("0 = EXIT PROGRAM")
print("-" * 35)

try:
    while True:
        if keyboard.is_pressed("6"):
            running = True
            print(f"▶ RUNNING | Mode: {mode.upper()}")
            time.sleep(0.3)

        if keyboard.is_pressed("7"):
            running = False
            print("⏸ PAUSED")
            time.sleep(0.3)

        if keyboard.is_pressed("8"):
            mode = "click"
            print("🖱 MODE: CLICK MOUSE")
            time.sleep(0.3)

        if keyboard.is_pressed("9"):
            mode = "key"
            print(f"⌨ MODE: PRESS KEY ({target_key.upper()})")
            time.sleep(0.3)

        if keyboard.is_pressed("0"):
            print("❌ EXITING...")
            break

        if not running:
            time.sleep(0.01)
            continue

        screenshot = pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

        found_any = False
        clicked_positions.clear()

        for name, template in templates:
            w, h = template.shape[::-1]
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= 0.80)

            for pt in zip(*loc[::-1]):
                x = pt[0] + w // 2
                y = pt[1] + h // 2

                if is_close((x, y), clicked_positions):
                    continue

                found_any = True
                clicked_positions.append((x, y))

                if mode == "click":
		    # ======SETING SEBERAPA CEPAT MOUSE BERPINDAH=======
                    pyautogui.moveTo(x, y, duration=0.01)
                    time.sleep(0.01)
		    #=======SETING SEBERAPA CEPAT MOUSE KLIK ==========
                    pyautogui.mouseDown()
                    time.sleep(0.01)
                    pyautogui.mouseUp()
                else:
                    # Mode Key: Tekan tombol sesuai jumlah yang diatur
                    for _ in range(key_press_count):
                        keyboard.press_and_release(target_key)
                    
                    # MEMBERI JEDA agar tidak mendeteksi gambar yang sama berulang kali
                    time.sleep(cooldown_after_key) 
                    break # Keluar dari loop koordinat untuk scan ulang layar baru

                time.sleep(0.01)
	# ===========SETING SEBERAPA CEPAT SCAN GAMBAR DI MONITOR =====
        if not found_any:
            time.sleep(0.01)

except Exception as e:
    print("Runtime error:", e)