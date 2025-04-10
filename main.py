import subprocess
import time
import numpy as np
import cv2
from datetime import datetime
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox

isFirstTime = False

CLICK_POSITIONS = {
    'agree_button': (685, 310),  # ตำแหน่งปุ่มตกลง
    'allow_button': (631, 328),
    'sign_in_apple': (644, 425),
    'guest_button': (480, 490),  # ตำแหน่งปุ่ม Guest Sign In
    'check_box_1' : (931,134),
    'check_box_2' : (930,248),
    'check_box_3' : (928,326),
    'agree' : (428,403),
    'return' : (686,472),
    'login_with_guest' : (550, 404),
    'first_load_data' : (583, 509),
    'select_language' : (377, 260),
    'ok' : (478, 422),
    'create_name': (476, 405),
    'name_as': (556, 406),
    'complete_name': (481, 359),
    'skip': (773, 28),
    'start_btn_skip': (553, 361),
    'click' : (470, 268),
    'first_ranger': (276, 473),
    'second_ranger': (380, 476),
    'third_ranger': (481, 477),
    'fourth_ranger': (581, 473),
    'missile': (152, 465),
    'mineral' : (812, 471),
    'stage_mode': (480, 98),
    'select_stage_1': (679, 445),
    'select_stage_2': (478, 266),
    'start_stage'   :  (480, 476),
    'select_meteor' : (185, 359),
    'use_meteor' : (46, 46),
    'receive_level' : (475, 454),
    'gacha_btn' : (662, 115),
    'random_character' : (360, 450),
    'confirm_random_character' : (554, 406),
    'receive_character': (396, 440),
    'select_team': (187, 473),
    'team_save_btn': (550, 359),
    'load_resource': (475, 360),
    'load_additional_resource': (554, 385),
    'close_large_popup': (816, 60),
    'close_medium_popup': (859, 36),
    'close_small_popup' : (816, 39),
    'setting_btn': (847, 500),
    'account_menu': (708, 91),
    'account_setting': (566, 421),
    'delete_account_btn': (474, 263),
    'delete_left_side': (331, 346),
    'delete_valid_1' : (400, 428),
    'delete_valid_2' : (553, 429),
    'delete_valid_3' : (400, 428),
    'delete_valid_4' : (659, 430),
    'delete_account' : (475, 407),
    'load_login_completed'  : (44, 507),
    'load_tutorial_completed' : (14, 526),
    'load_resource_completed' : (143, 416), 
    'load_game_with_ticket' : (246, 439),
    'load_gacha_page_success' : (151, 386),
    'close_popup_completed' : (544, 286), 
    'slot' : (475, 454),
    'open_teasure': (442, 143),
    'receive_ticket': (476, 418),
    'enter_7days' : (917, 238),
    'receive_7days_ticket' : (336, 445),
    'receive_7days_ticket_success' : (486, 408),
    'open_gift_box' : (764, 463),
    'receive_all_btn' : (697, 464),
    'receive_all' : (554, 359),
    'receive_all_success' : (478, 359),
    'close_7days_popup' : (839, 40),
    'back_btn' : (31, 27),
    
}

def check_special_days(date=None):
    """
    ตรวจสอบว่าวันที่ระบุเป็นวันอังคาร, เสาร์, หรืออาทิตย์
    ถ้าไม่ระบุวันที่ จะใช้เวลาปัจจุบัน
    """
    # ถ้าไม่ระบุวันที่ ใช้เวลาปัจจุบัน
    if date is None:
        date = datetime.now()
    
    # ดึงค่า weekday (0 = จันทร์, 1 = อังคาร, ..., 6 = อาทิตย์)
    weekday = date.weekday()
    
    # ตรวจสอบและคืนค่าผลลัพธ์
    if weekday == 1:  # อังคาร
        return True, "วันอังคาร"
    elif weekday == 5:  # เสาร์
        return True, "วันเสาร์"
    elif weekday == 6:  # อาทิตย์
        return True, "วันอาทิตย์"
    else:
        return False, "ไม่ใช่วันอังคาร, เสาร์, หรืออาทิตย์"
    
def get_emulators():
    try:
        result = subprocess.check_output("adb devices", shell=True).decode()
        lines = result.strip().split("\n")[1:]
        emulators = [line.split()[0] for line in lines if "emulator" in line and "device" in line]
        return emulators
    except subprocess.CalledProcessError as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึง emulator: {e}")
        return []

def press_back_button(device):
    print(f"🔙 กดปุ่มกลับบน {device}")
    adb_shell(device, "input keyevent 4")  # คำสั่งสำหรับกดปุ่มกลับ
    time.sleep(1)  # รอให้คำสั่งสำเร็จ

def adb_shell(device, cmd):
    subprocess.run(f"adb -s {device} shell {cmd}", shell=True)

def click(device, x, y):
    adb_shell(device, f"input tap {x} {y}")
    
def click_with_delay(device, x, y, delay_after=1):
    print(f"🖱️ [Device: {device}] คลิกที่ ({x}, {y}) - รอ {delay_after} วินาที")
    click(device, x, y)  # เพิ่มคำสั่งคลิกจริง
    time.sleep(delay_after)    

def screencap(device):
    cap1 = subprocess.check_output(f'adb -s {device} exec-out screencap -p', shell=True)
    image = np.frombuffer(cap1, dtype=np.uint8)
    img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return img

def check_app_status(device):
    result = subprocess.check_output(f"adb -s {device} shell dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'", shell=True).decode()
    if "com.linecorp.LGRGS" in result:
        print("✅ แอปพลิเคชันกำลังทำงาน")
        return True
    else:
        print("❌ แอปพลิเคชันไม่ทำงาน")
        return False
    
def check_pixel_color(device, x, y, expected_color, tolerance=10):
    """
    ตรวจสอบสีที่ตำแหน่ง (x,y)
    expected_color: (B, G, R)
    tolerance: ค่าความคลาดเคลื่อนที่ยอมรับได้
    """
    img = screencap(device)
    pixel = img[y, x]
    
    return (abs(pixel[0] - expected_color[0]) <= tolerance and
            abs(pixel[1] - expected_color[1]) <= tolerance and
            abs(pixel[2] - expected_color[2]) <= tolerance)

def wait_for_load(device, x, y, expected_color, timeout=60, interval=1):
    """
    รอจนกว่าพิกเซลที่ตำแหน่ง (x, y) จะมีสีตามที่คาดหวัง
    - device: ชื่ออุปกรณ์ emulator
    - x, y: ตำแหน่งพิกเซล
    - expected_color: ค่า BGR ที่คาดหวัง (เช่น [255, 255, 255])
    - timeout: จำนวนวินาทีสูงสุดที่รอ
    - interval: ระยะห่างระหว่างการตรวจสอบ (วินาที)
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_pixel_color(device, x, y, expected_color):
            print(f"✅ โหลดเสร็จแล้วที่ตำแหน่ง ({x}, {y})")
            return True
        print(f"⏳ รอโหลดที่ ({x}, {y})...")
        time.sleep(interval)
    print(f"❌ หมดเวลา! โหลดไม่เสร็จใน {timeout} วินาที")
    return False

def delete_account(device):
    """ลบแอคเคาท์แบบอิสระในแต่ละเครื่อง"""
    try:
        print(f"\n🗑️ [Device: {device}] เริ่มกระบวนการลบแอคเคาท์...")
        
        # ขั้นตอนที่ 1: เข้าเมนูตั้งค่า
        click_with_delay(device, *CLICK_POSITIONS['setting_btn'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['account_menu'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['account_setting'], delay_after=5)
        
        # ขั้นตอนที่ 2: เริ่มกระบวนการลบ
        click_with_delay(device, *CLICK_POSITIONS['delete_account_btn'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['delete_left_side'], delay_after=5)
        
        # ขั้นตอนที่ 3: ยืนยันการลบ
        click_with_delay(device, *CLICK_POSITIONS['delete_valid_1'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['delete_valid_2'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['delete_valid_3'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['delete_valid_4'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['delete_account'], delay_after=5)
        
        print(f"✅ [Device: {device}] ลบแอคเคาท์สำเร็จ")
        return True
        
    except Exception as e:
        print(f"🔴 [Device: {device}] เกิดข้อผิดพลาดขณะลบแอคเคาท์: {e}")
        return False

def play_until_load_data(device):
    """เล่นเกมจนโหลดข้อมูลเสร็จแบบอิสระในแต่ละเครื่อง"""
    try:
        print(f"\n🎮 [Device: {device}] เริ่มเล่นเกมจนโหลดข้อมูลเสร็จ...")
        
        # ตรวจสอบหน้าจอเริ่มต้น
        if not wait_for_load(device, *CLICK_POSITIONS['load_tutorial_completed'], expected_color=[57, 60, 66], timeout=60):
            print(f"🔴 [Device: {device}] ไม่พบหน้าจอเริ่มต้น")
            return False

        # ขั้นตอนที่ 1: ข้ามและเริ่มเกม
        click_with_delay(device, *CLICK_POSITIONS['skip'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=10)
        
        # ขั้นตอนที่ 2: เลือกโหมดและสเตจ
        click_with_delay(device, *CLICK_POSITIONS['stage_mode'], delay_after=10)
        click_with_delay(device, *CLICK_POSITIONS['select_stage_1'], delay_after=10)
        
        # ขั้นตอนที่ 3: คลิกเตรียมตัว
        for _ in range(5):
            click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=1)
        time.sleep(10)
        
        # ขั้นตอนที่ 4: เริ่มสเตจ
        click_with_delay(device, *CLICK_POSITIONS['start_stage'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['select_meteor'], delay_after=10)
        click_with_delay(device, *CLICK_POSITIONS['first_ranger'], delay_after=5)
        
        # ขั้นตอนที่ 5: โจมตีศัตรู
        for _ in range(5):
            click_with_delay(device, *CLICK_POSITIONS['first_ranger'], delay_after=2)
            click_with_delay(device, *CLICK_POSITIONS['second_ranger'], delay_after=2)
            click_with_delay(device, *CLICK_POSITIONS['third_ranger'], delay_after=2)
            click_with_delay(device, *CLICK_POSITIONS['fourth_ranger'], delay_after=2)

        click_with_delay(device, *CLICK_POSITIONS['use_meteor'], delay_after=30)

        # ขั้นตอนที่ 6: รับรางวัล
        click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['receive_level'], delay_after=5)
        
        for _ in range(4):
            click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=2)
        
        # ขั้นตอนที่ 7: ระบบกาชา
        click_with_delay(device, *CLICK_POSITIONS['skip'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['gacha_btn'], delay_after=10)
        click_with_delay(device, *CLICK_POSITIONS['random_character'], delay_after=10)
        click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=2)
        click_with_delay(device, *CLICK_POSITIONS['receive_character'], delay_after=10)
        
        # ขั้นตอนที่ 8: ทีมและโหลดข้อมูล
        click_with_delay(device, *CLICK_POSITIONS['skip'], delay_after=10)
        click_with_delay(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=10)
        click_with_delay(device, *CLICK_POSITIONS['select_team'], delay_after=10)
        
        for _ in range(4):
            click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=3)
        
        swipe_screen(device, 479, 204, 383, 436)
        time.sleep(10)
        swipe_screen(device, 110, 448, 482, 193)
        time.sleep(10)
        
        click_with_delay(device, *CLICK_POSITIONS['skip'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['team_save_btn'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['skip'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=5)
        
        # ขั้นตอนสุดท้าย: โหลดข้อมูล
        click_with_delay(device, *CLICK_POSITIONS['load_resource'], delay_after=20)
        click_with_delay(device, *CLICK_POSITIONS['load_additional_resource'], delay_after=5)
        time.sleep(20)
        print(f"✅ [Device: {device}] เล่นเกมจนโหลดข้อมูลเสร็จสมบูรณ์")
        return True
        
    except Exception as e:
        print(f"🔴 [Device: {device}] เกิดข้อผิดพลาดขณะเล่นเกม: {e}")
        return False
    
def login_with_guestID(device):
    """ล็อกอินแบบ Guest โดยแต่ละเครื่องทำงานอิสระ"""
    try:
        print(f"\n🔵 [Device: {device}] เริ่มกระบวนการล็อกอิน...")
        
        # ขั้นตอนที่ 1: หน้าต้อนรับ
        time.sleep(15)
        click_with_delay(device, *CLICK_POSITIONS['agree_button'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['allow_button'], delay_after=5)
        
        # ขั้นตอนที่ 2: ล็อกอินครั้งแรก
        click_with_delay(device, *CLICK_POSITIONS['sign_in_apple'], delay_after=5)
        for pos in ['check_box_1', 'check_box_2', 'check_box_3']:
            click_with_delay(device, *CLICK_POSITIONS[pos], delay_after=2)

        click_with_delay(device, *CLICK_POSITIONS['agree'], delay_after=5)
        
        # ย้อนกลับและลองใหม่
        press_back_button(device)
        time.sleep(3)
        click_with_delay(device, *CLICK_POSITIONS['sign_in_apple'], delay_after=2)
        for pos in ['check_box_1', 'check_box_2', 'check_box_3']:
            click_with_delay(device, *CLICK_POSITIONS[pos], delay_after=2)
        click_with_delay(device, *CLICK_POSITIONS['agree'], delay_after=5)
        press_back_button(device)
        time.sleep(3)
        
        # ขั้นตอนที่ 3: ล็อกอินแบบ Guest
        click_with_delay(device, *CLICK_POSITIONS['guest_button'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['login_with_guest'], delay_after=5)
        for pos in ['check_box_1', 'check_box_2', 'check_box_3']:
            click_with_delay(device, *CLICK_POSITIONS[pos], delay_after=3)

        click_with_delay(device, *CLICK_POSITIONS['agree'], delay_after=10)
        
        # ขั้นตอนที่ 4: ตั้งค่าหลังล็อกอิน
        click_with_delay(device, *CLICK_POSITIONS['first_load_data'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['select_language'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['ok'], delay_after=40)
        click_with_delay(device, *CLICK_POSITIONS['create_name'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['name_as'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['complete_name'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['skip'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=5)
        time.sleep(20)
        print(f"🟢 [Device: {device}] ล็อกอินสำเร็จทั้งหมด")
        return True
        
    except Exception as e:
        print(f"🔴 [Device: {device}] เกิดข้อผิดพลาด: {e}")
        return False

def play_tutorial(device):
    """เล่น Tutorial แบบอิสระในแต่ละเครื่อง"""
    try:
        print(f"\n🎮 [Device: {device}] เริ่มเล่น Tutorial...")
        
        # 1. ตรวจสอบหน้าจอโหลดเสร็จ
        if not wait_for_load(device, *CLICK_POSITIONS['load_login_completed'], expected_color=[0, 0, 0], timeout=60):
            print(f"🔴 [Device: {device}] ไม่พบหน้าจอ Tutorial")
            return False

        # 2. ขั้นตอนคลิกเริ่มต้น
        for _ in range(4):
            click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=1)

        # 3. เลือกตัวละคร
        click_with_delay(device, *CLICK_POSITIONS['first_ranger'], delay_after=2)
        click_with_delay(device, *CLICK_POSITIONS['second_ranger'], delay_after=2)
        click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=4)

        # 4. เก็บทรัพยากร
        for _ in range(3):
            click_with_delay(device, *CLICK_POSITIONS['mineral'], delay_after=3)
        click_with_delay(device, *CLICK_POSITIONS['mineral'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=2)

        # 5. เลือกตัวละครเพิ่ม
        click_with_delay(device, *CLICK_POSITIONS['third_ranger'], delay_after=2)
        click_with_delay(device, *CLICK_POSITIONS['fourth_ranger'], delay_after=2)

        # 6. ใช้สกิล
        for _ in range(5):
            click_with_delay(device, *CLICK_POSITIONS['missile'], delay_after=2)

        # 7. คลิกต่อเนื่อง
        for _ in range(10):
            click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=1)

        # 8. โจมตีศัตรู
        for _ in range(25):
            click_with_delay(device, *CLICK_POSITIONS['third_ranger'], delay_after=2)
            click_with_delay(device, *CLICK_POSITIONS['fourth_ranger'], delay_after=2)

        print(f"✅ [Device: {device}] เล่น Tutorial เสร็จสิ้น")
        time.sleep(20)
        return True

    except Exception as e:
        print(f"🔴 [Device: {device}] เกิดข้อผิดพลาดขณะเล่น Tutorial: {e}")
        return False

def play_until_level_3(device):
    if not wait_for_load(device, *CLICK_POSITIONS['load_resource_completed'], expected_color=[24, 211, 255], timeout=60):
            print(f"🔴 [Device: {device}] โหลดทรัพยากรล้มเหลว")
            return False
    
    click_with_delay(device, *CLICK_POSITIONS['stage_mode'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['select_stage_2'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['start_stage'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['use_meteor'], delay_after=5)

    for _ in range(5):
            click_with_delay(device, *CLICK_POSITIONS['first_ranger'], delay_after=2)
            click_with_delay(device, *CLICK_POSITIONS['second_ranger'], delay_after=2)
            click_with_delay(device, *CLICK_POSITIONS['third_ranger'], delay_after=2)
            click_with_delay(device, *CLICK_POSITIONS['fourth_ranger'], delay_after=2)


    for _ in range(2):
        click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=5)

    click_with_delay(device, *CLICK_POSITIONS['receive_level'], delay_after=7)

    for _ in range(4):
        click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=2)

    for _ in range(3):
        click_with_delay(device, *CLICK_POSITIONS['slot'], delay_after=2)    

    click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=5)

    click_with_delay(device, *CLICK_POSITIONS['skip'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['stage_mode'], delay_after=12)
    click_with_delay(device, *CLICK_POSITIONS['open_teasure'], delay_after=5)

    for _ in range(3):
        click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=5)
    restart_all_emulators()
    close_popup()

def receive_7days(device):
    if not wait_for_load(device, *CLICK_POSITIONS['load_resource_completed'], expected_color=[24, 211, 255], timeout=60):
            print(f"🔴 [Device: {device}] โหลดทรัพยากรล้มเหลว")
            return False
    click_with_delay(device, *CLICK_POSITIONS['enter_7days'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['receive_7days_ticket'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['receive_7days_ticket_success'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['close_7days_popup'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['open_gift_box'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['receive_all_btn'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['receive_all'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['receive_all_success'], delay_after=5)

    click_with_delay(device, *CLICK_POSITIONS['close_small_popup'], delay_after=5)


def summon_rangers(device,round):
    click_with_delay(device, *CLICK_POSITIONS['gacha_btn'], delay_after=5)
    if not wait_for_load(device, *CLICK_POSITIONS['load_gacha_page_success'], expected_color=[107, 36, 107], timeout=60):
            print(f"🔴 [Device: {device}] โหลดทรัพยากรล้มเหลว")
            return False
    for _ in range(round):
        click_with_delay(device, *CLICK_POSITIONS['random_character'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['confirm_random_character'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['receive_character'], delay_after=5)
    click_with_delay(device, *CLICK_POSITIONS['back_btn'], delay_after=5)

def restart_game(device):
    """
    รีเกมเข้าใหม่โดยไม่ลบข้อมูลเกม
    - device: ชื่ออุปกรณ์ emulator
    """
    try:
        print(f"\n🔄 [Device: {device}] กำลังรีเกมเข้าใหม่...")
        
        # 1. ปิดเกม
        print(f"⏹ [Device: {device}] กำลังปิดแอปเกม...")
        adb_shell(device, "am force-stop com.linecorp.LGRGS")
        time.sleep(3)
        
        # 2. เปิดเกมใหม่
        print(f"🚀 [Device: {device}] กำลังเปิดแอปเกมใหม่...")
        adb_shell(device, "monkey -p com.linecorp.LGRGS -c android.intent.category.LAUNCHER 1")
        time.sleep(15)  # รอให้เกมโหลด
        
        # 3. ตรวจสอบว่าเข้าสู่เกมแล้ว
        if check_app_status(device):
            print(f"✅ [Device: {device}] รีเกมสำเร็จ")
            return True
        else:
            print(f"❌ [Device: {device}] ไม่สามารถเปิดเกมได้")
            return False
            
    except Exception as e:
        print(f"⚠️ [Device: {device}] เกิดข้อผิดพลาดขณะรีเกม: {e}")
        return False

def close_popup(device):
    if not wait_for_load(device, *CLICK_POSITIONS['load_game_with_ticket'], expected_color=[33, 65, 123], timeout=60):
            print(f"🔴 [Device: {device}] ไม่พบหน้าจอ Tutorial")
            return False
    for _ in range(10):
        click_with_delay(device, *CLICK_POSITIONS['receive_ticket'], delay_after=2)
    for _ in range(15):
        click_with_delay(device, *CLICK_POSITIONS['close_medium_popup'], delay_after=1)
        click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=1)
    
    if not wait_for_load(device, *CLICK_POSITIONS['close_popup_completed'], expected_color=[107, 138, 189], timeout=60):
            print(f"🔴 [Device: {device}] ปิด popup ล้มเหลว")
            return False
    time.sleep(5)

def restart_all_emulators():
    """
    รีเกมใหม่ทุกเครื่องพร้อมกันโดยไม่ลบข้อมูล
    """
    emulators = get_emulators()
    if not emulators:
        print("❌ ไม่พบ Emulator ที่เปิดอยู่")
        return
    
    threads = []
    for device in emulators:
        thread = threading.Thread(
            target=restart_game,
            args=(device,),
            name=f"RestartThread-{device}"
        )
        threads.append(thread)
        thread.start()
        time.sleep(1)  # เว้นระยะเริ่มต้นแต่ละเครื่อง
    
    print(f"🔄 กำลังรีเกมบน {len(emulators)} เครื่อง...")
    
    # รอให้ทุกเธรดทำงานเสร็จ
    for thread in threads:
        thread.join()
    
    print("✅ รีเกมทุกเครื่องเสร็จสิ้น")

def re_id(device):
    try:
        package = "com.linecorp.LGRGS"
        if isFirstTime == False:
            print(f"🧹 ล้างข้อมูล {device}")
            adb_shell(device, f"pm clear {package}")
            time.sleep(2)
        print(f"🚀 เปิดเกม {device}")
        adb_shell(device, f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
        time.sleep(10)
        print(f"🚀 เริ่มรีไอดี {device}")
        isFirstTime == True
        login_with_guestID(device)
        play_tutorial(device)
        play_until_load_data(device)
        # delete_account(device)
        debug_pixel(device)
        
        if check_special_days(): 
            play_until_level_3(device)
        if not check_special_days():
            close_popup(device)
        receive_7days(device)
        summon_rangers(device,2)
        
        img = screencap(device)
        cv2.imwrite(f"{device}_screenshot.jpg", img)
        print(f"✅ รีไอดีเสร็จ {device} กำลังดำเนินการลบไอดี")
        # delete_account(device)
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดใน re_id บน {device}: {str(e)}")

def debug_pixel(device):
    print(f"\n🔍 เริ่ม Debug ค่า Pixel บน {device}")
    
    # ใช้ตัวแปร img แบบ global เพื่ออัปเดตค่าของภาพใน mouse_callback
    img = screencap(device)
    
    # ส่งภาพไปให้ mouse_callback ผ่าน param
    def mouse_callback(event, x, y, flags, param):
        img = param[0]  # ดึงค่า img จาก param[0]
        if event == cv2.EVENT_LBUTTONDOWN:
            pixel = img[y, x]
            print(f"ตำแหน่ง: ({x}, {y}) | ค่า BGR: {pixel}")
            print(f"ตัวอย่างคำสั่งเพิ่มตำแหน่ง: 'new_position': ({x}, {y})")
            
            # รีเฟรชหน้าจอหลังจากคลิก
            img = screencap(device)
            # อัปเดต param ให้เป็นภาพใหม่
            param[0] = img

    cv2.namedWindow('Debug Pixel', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Debug Pixel', 800, 600)
    
    # ใช้ param เพื่อส่งภาพให้ mouse_callback
    cv2.setMouseCallback('Debug Pixel', mouse_callback, param=[img])
    
    while True:
        cv2.imshow('Debug Pixel', img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cv2.destroyAllWindows()
    print(f"🔚 จบการ Debug บน {device}")

def swipe_screen(device, start_x, start_y, end_x, end_y, duration=1000):
    print(f"🖱️ ลากหน้าจอจาก ({start_x}, {start_y}) ไปยัง ({end_x}, {end_y}) ใช้เวลา {duration} ms")
    adb_shell(device, f"input swipe {start_x} {start_y} {end_x} {end_y} {duration}")
    time.sleep(1)  # รอให้การลากเสร็จ

def run_all_independent():
    """รันแต่ละเครื่องแบบอิสระ"""
    emulators = get_emulators()
    if not emulators:
        print("❌ ไม่พบ Emulator ที่เปิดอยู่")
        return
    
    threads = []
    for device in emulators:
        thread = threading.Thread(
            target=re_id,  # เปลี่ยนจาก run_with_monitoring เป็น re_id โดยตรง
            args=(device,),
            name=f"Thread-{device}"
        )
        threads.append(thread)
        thread.start()
        time.sleep(1)  # เว้นระยะเริ่มต้นแต่ละเครื่อง
    
    print(f"🚀 เริ่มทำงานบน {len(emulators)} เครื่อง...")
    
    # รอให้ทุกเธรดทำงานเสร็จ
    for thread in threads:
        thread.join()

def process_device_independent(device):
    """กระบวนการสำหรับแต่ละเครื่องแบบอิสระ"""
    try:
        print(f"\n⚙️ [Device: {device}] เริ่มทำงาน...")
        re_id(device)
    except Exception as e:
        print(f"❌ [Device: {device}] เกิดข้อผิดพลาด: {e}")

running = False

# ===== GUI Setup =====
def log(msg):
    output_text.config(state='normal')
    output_text.insert(tk.END, f"{msg}\n")
    output_text.see(tk.END)
    output_text.config(state='disabled')

def start_bot_thread():
    thread = threading.Thread(target=start_bot, daemon=True)
    thread.start()

def start_bot():
    global running
    running = True
    log("เริ่มทำงานบอท...")
    run_all_independent()
    while running:
        log("บอทกำลังทำงาน...")
        time.sleep(2)

def stop_bot():
    global running
    running = False
    log("หยุดการทำงานของบอทแล้ว")

# ===== GUI Setup =====
def log(msg):
    output_text.config(state='normal')
    output_text.insert(tk.END, f"{msg}\n")
    output_text.see(tk.END)
    output_text.config(state='disabled')

def start_bot_thread():
    thread = threading.Thread(target=start_bot, daemon=True)
    thread.start()

# ===== สร้าง GUI =====
root = tk.Tk()
root.title("Emulator Bot Controller")
root.geometry("500x450")

frame = ttk.Frame(root)
frame.pack(pady=10)

start_btn = ttk.Button(frame, text="▶ เริ่มบอท", command=start_bot_thread)
start_btn.grid(row=0, column=0, padx=5)

stop_btn = ttk.Button(frame, text="⏹ หยุดบอท", command=stop_bot)
stop_btn.grid(row=0, column=1, padx=5)

# แสดง Log ด้านล่าง
output_text = scrolledtext.ScrolledText(root, height=18, state='disabled')
output_text.pack(fill='both', expand=True, padx=10, pady=10)

root.mainloop()