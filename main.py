import subprocess
import time
import numpy as np
import cv2
from datetime import datetime
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import math
import os
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import Image
from tkinter import font as tkfont

monitoring_active = True  # ค่าเริ่มต้น
isLoadResource = True
running = False
summon_times = 0
running = False
target_characters = []
choice = '1'
excluded_devices = []
skip_7days = False
random_summon = True
delay = 3
select_gacha_number = ['common','rate-up(1)','rate-up(2)']
isFirstTime  = True
isFound = False

CLICK_POSITIONS = {
    'agree_button': (685, 310),  # ตำแหน่งปุ่มตกลง
    'allow_button': (631, 328),
    'sign_in_apple': (642, 425),
    'guest_button': (568, 498),
    'check_box_1' : (931,134),
    'check_box_2' : (930,248),
    'check_box_3' : (928,326),
    'agree' : (430, 404),
    'return' : (686,472),
    'login_with_guest' : (550, 404),
    'first_load_data' : (606, 516),
    'select_language' : (362, 262),
    'ok' : (522, 425),
    'create_name': (476, 405),
    'name_as': (601, 407),
    'complete_name': (529, 361),
    'skip': (773, 27),
    'start_btn_skip': (595, 370),
    'click' : (470, 268),
    'first_ranger': (292, 477),
    'second_ranger': (382, 486),
    'third_ranger': (488, 479),
    'fourth_ranger': (583, 475),
    'missile': (152, 465),
    'missile_common': (154, 462),
    'mineral' : (811, 461),
    'stage_mode': (481, 79),
    'select_stage_1': (486, 480),
    'select_stage_1_tutorial': (686, 449),
    'select_stage_2': (478, 266),
    'start_stage'   :  (478, 94),
    'start_stage_1_tutorial': (592, 476),
    'used_meteor_tutorial' : (44, 56), 
    'select_meteor' : (185, 359),  
    'use_meteor' : (46, 46),
    'receive_level' : (475, 454),
    'gacha_btn' : (662, 115),
    'random_character' : (360, 450),
    'confirm_random_character' : (554, 406),
    'receive_character': (353, 437),
    'select_team': (187, 473),
    'team_save_btn': (550, 359),
    'load_resource': (475, 360),
    'load_additional_resource': (595, 386),
    'close_large_popup': (816, 60),
    'close_medium_popup': (859, 36),
    'close_small_popup' : (816, 39),
    'setting_btn': (847, 500),
    'account_menu': (708, 91),
    'account_setting': (566, 421),
    'delete_account_btn': (594, 264),
    'delete_left_side': (331, 346),
    'delete_valid_1' : (353, 428),
    'delete_valid_2' : (588, 428), 
    'delete_valid_3' : (353, 428),
    'delete_valid_4' : (630, 428), 
    'delete_account' : (648, 425),
    'deleted_success' : (515, 400),
    'load_login_completed'  : (44, 507),
    'load_tutorial_completed' : (14, 526),
    'load_resource_completed' : (143, 416), 
    'load_game_with_ticket' : (246, 439),
    'load_game_with_calendar' : (360, 346),
    'load_gacha_page_success' : (151, 386),
    'load_stage' : (40, 515),
    'play_stage_success': (143, 490),
    'close_popup_completed' : (544, 286), 
    'slot' : (475, 454),
    'open_teasure': (442, 143),
    'receive_ticket': (476, 418),
    'enter_7days' : (902, 240),
    'receive_7days_ticket' : (336, 445),
    'receive_7days_ticket_success' : (486, 408),
    'open_gift_box' : (764, 463),
    'receive_all_btn' : (774, 465) ,
    'receive_all' : (589, 359),
    'receive_all_success' : (516, 355),
    'close_7days_popup' : (840, 37) ,
    'back_btn' : (31, 27),
    'close_calendar': (812, 61),
    'is_black_screen': (812, 61),
    'click_ticket' : (478, 417),
    'random_character_gacha' : (188, 440),
    'confirm_random_gacha' : (606, 405),
    'select_eng_lang' : (606, 405) ,
    'is_gray_screen' : (674, 417) ,
    'is_network_lost': (522, 362) ,
    'close_largest_popup': (928, 30),
    'close_show_event' : (859, 36),
    'select_first_gacha' : (835, 177),
    'select_second_gacha' : (827, 313),
    'select_third_gacha' : (833, 441),
    'close_buff_event' : (814, 37) ,
    'close_gift_popup' : (803,33),
}
# process
def get_emulators():
    """Get list of connected emulators excluding excluded_devices"""
    try:
        result = subprocess.check_output("adb devices", shell=True).decode()
        lines = result.strip().split("\n")[1:]
        emulators = [line.split()[0] for line in lines 
                    if "emulator" in line and "device" in line
                    and line.split()[0] not in excluded_devices]
        return emulators
    except subprocess.CalledProcessError as e:
        log(f"❌ Failed to get emulators: {str(e)}")
        return []

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
            args=(device,True),
            name=f"Thread-{device}"
        )
        threads.append(thread)
        thread.start()
        time.sleep(5)  
    
    print(f"🚀 เริ่มทำงานบน {len(emulators)} เครื่อง...")
    
    # รอให้ทุกเธรดทำงานเสร็จ
    for thread in threads:
        thread.join()

def process_device_independent(device):
    """กระบวนการสำหรับแต่ละเครื่องแบบอิสระ"""
    try:
        print(f"\n⚙️ [Device: {device}] เริ่มทำงาน...")
        re_id(device,True)
    except Exception as e:
        print(f"❌ [Device: {device}] เกิดข้อผิดพลาด: {e}")

def adb_shell(device, command):
    return os.system(f"adb -s {device} shell {command}")
# main feature
def re_id(device, isFirstTime=True,max_retries=5, current_retry=0):

    if current_retry >= max_retries:
        print(f"❌ ถึงจำนวนครั้งสูงสุดที่ลองแล้ว {device}")
        return False
     
    flag = 1
    if choice == '1':
        try:
            package = "com.linecorp.LGRGS"
            if isFirstTime:
                print(f"🧹 ล้างข้อมูล {device}")
                adb_shell(device, f"pm clear {package}")
                time.sleep(2)
            print(f"🚀 เปิดเกม {device}")
            adb_shell(device, f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
            print(f"🚀 เริ่มรีไอดี {device}")
            if isFirstTime:
                login_with_guestID(device,isFirstTime = True)
            else :
                login_with_guestID(device,isFirstTime = False)
            play_tutorial(device)
            play_until_load_data(device)
            if check_special_days()[0]:
                close_popup(device, flag)
            else:
                play_until_level_3(device)
            receive_7days(device)
            print(isFound,isFirstTime)
            if summon_times > 0:
                summon_rangers(device, summon_times)
                log(f"🎯 ซัมมอนจำนวน {summon_times} ครั้ง")

            print(f"✅ รีไอดีเสร็จ {device} กำลังดำเนินการลบไอดี และรีใหม่")
            if not isFound:
                delete_account(device)
                return re_id(device, isFirstTime=False, max_retries=max_retries, current_retry=current_retry+1)
            else:
                return True  # ส่งค่ากลับเมื่อสำเร็จ

        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดใน re_id บน {device}: {str(e)}")
            return re_id(device, isFirstTime, max_retries, current_retry+1)
    else:
        debug_pixel(device)
        return False

def delete_account(device):
    """ลบแอคเคาท์แบบอิสระในแต่ละเครื่อง"""
    try:
        print(f"\n🗑️ [Device: {device}] เริ่มกระบวนการลบแอคเคาท์...")
        
        # ขั้นตอนที่ 1: เข้าเมนูตั้งค่า
        click_with_delayV2(device, *CLICK_POSITIONS['setting_btn'], delay_after=delay,expected_color=[140, 138, 156])
        click_with_delayV2(device, *CLICK_POSITIONS['account_menu'], delay_after=delay,expected_color=[ 33,  69, 140])
        click_with_delayV2(device, *CLICK_POSITIONS['account_setting'], delay_after=10,expected_color= [165, 178, 206])
        
        # ขั้นตอนที่ 2: เริ่มกระบวนการลบ
        click_with_delay(device, *CLICK_POSITIONS['delete_account_btn'], delay_after=delay)
        click_with_delayV2(device, *CLICK_POSITIONS['delete_left_side'], delay_after=delay,expected_color= [33, 69, 140])

        # ขั้นตอนที่ 3: ยืนยันการลบ
        click_with_delayV2(device, *CLICK_POSITIONS['delete_valid_1'], delay_after=delay,expected_color=[49, 195,0])
        click_with_delayV2(device, *CLICK_POSITIONS['delete_valid_2'], delay_after=delay,expected_color=[ 49, 195, 0])
        click_with_delayV2(device, *CLICK_POSITIONS['delete_valid_3'], delay_after=delay,expected_color=[49, 195,0])
        click_with_delay(device, *CLICK_POSITIONS['delete_valid_4'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['delete_account'], delay_after=delay )
        click_with_delayV2(device, *CLICK_POSITIONS['deleted_success'], delay_after=delay,expected_color=  [ 49, 195, 0])

      
        print(f"✅ [Device: {device}] ลบแอคเคาท์สำเร็จ")

        return True
        
    except Exception as e:
        print(f"🔴 [Device: {device}] เกิดข้อผิดพลาดขณะลบแอคเคาท์: {e}")
        return False

def play_until_load_data(device):
    """เล่นเกมจนโหลดข้อมูลเสร็จแบบอิสระในแต่ละเครื่อง"""
    try:
        print(f"\n🎮 [Device: {device}] เริ่มเล่นเกมจนโหลดข้อมูลเสร็จ...")

        for _ in range(4):
            click_with_delayV2(device, *CLICK_POSITIONS['skip'], delay_after=3)
            click_with_delayV2(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=3)

        if not wait_for_load(device, *CLICK_POSITIONS['load_tutorial_completed'], expected_color=[57, 60, 66], timeout=90):
            print(f"🔴 [Device: {device}] ไม่พบหน้าจอเริ่มต้น")
            return False


        # ขั้นตอนที่ 2: เลือกโหมดและสเตจ
        click_with_delayV2(device, *CLICK_POSITIONS['stage_mode'], delay_after=10,expected_color=[49, 60, 66])
        click_with_delayV2(device, *CLICK_POSITIONS['select_stage_1_tutorial'], delay_after=10,expected_color= [107, 215, 247])

        for _ in range(5):
            click_with_delayV2(device, *CLICK_POSITIONS['click'], delay_after=2)
        

        # ขั้นตอนที่ 4: เริ่มสเตจ
        click_with_delayV2(device, *CLICK_POSITIONS['select_meteor'], delay_after=2,expected_color=[156, 190, 198])
        click_with_delayV2(device, *CLICK_POSITIONS['start_stage_1_tutorial'], delay_after=2,expected_color=[ 49, 195, 0])

        click_with_delayV2(device, *CLICK_POSITIONS['third_ranger'], delay_after=1)
        click_with_delayV2(device, *CLICK_POSITIONS['fourth_ranger'], delay_after=1)

        for _ in range(6):
            click_with_delay(device, *CLICK_POSITIONS['used_meteor_tutorial'], delay_after=3)

        # ขั้นตอนที่ 5: โจมตีศัตรู
        for _ in range(12):
            click_with_delayV2(device, *CLICK_POSITIONS['first_ranger'], delay_after=2)
            click_with_delayV2(device, *CLICK_POSITIONS['second_ranger'], delay_after=2)
            click_with_delayV2(device, *CLICK_POSITIONS['third_ranger'], delay_after=2)
            click_with_delayV2(device, *CLICK_POSITIONS['fourth_ranger'], delay_after=2)
        
        # ขั้นตอนที่ 6: รับรางวัล
        for _ in range(5):
             click_with_delayV2(device, *CLICK_POSITIONS['click'], delay_after=3)
       
        click_with_delayV2(device, *CLICK_POSITIONS['receive_level'], delay_after=5)

        for _ in range(5):
            click_with_delayV2(device, *CLICK_POSITIONS['click'], delay_after=2)
        
        # ขั้นตอนที่ 7: ระบบกาชา
        click_with_delayV2(device, *CLICK_POSITIONS['skip'], delay_after=3)
        click_with_delayV2(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=3)
        click_with_delayV2(device, *CLICK_POSITIONS['gacha_btn'], delay_after=3,expected_color=[189, 178,189])
        click_with_delayV2(device, *CLICK_POSITIONS['random_character'], delay_after=3,expected_color= [ 66,255, 255])
        click_with_delayV2(device, *CLICK_POSITIONS['click'], delay_after=2)
        click_with_delayV2(device, *CLICK_POSITIONS['receive_character'], delay_after=3,expected_color=[ 49, 195,  0])
        
        # ขั้นตอนที่ 8: ทีมและโหลดข้อมูล
        click_with_delayV2(device, *CLICK_POSITIONS['skip'], delay_after=3,)
        click_with_delayV2(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=3,)
        click_with_delayV2(device, *CLICK_POSITIONS['select_team'], delay_after=3,expected_color=[  0, 109, 198])
        
        for _ in range(4):
            click_with_delayV2(device, *CLICK_POSITIONS['click'], delay_after=3)
        
        swipe_screen(device, 479, 204, 383, 436)
        time.sleep(10)
        swipe_screen(device, 110, 448, 482, 193)
        time.sleep(10)
        
        click_with_delayV2(device, *CLICK_POSITIONS['skip'], delay_after=3,)
        click_with_delayV2(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=3,)
        click_with_delayV2(device, *CLICK_POSITIONS['team_save_btn'], delay_after=3,expected_color=[255, 255, 255])
      

        for _ in range(4):
            click_with_delayV2(device, *CLICK_POSITIONS['skip'], delay_after=3)
            click_with_delayV2(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=3)
        
        # ขั้นตอนสุดท้าย: โหลดข้อมูล
        click_with_delayV2(device, *CLICK_POSITIONS['load_resource'], delay_after=10,expected_color=[255,255, 255])
        click_with_delayV2(device, *CLICK_POSITIONS['load_additional_resource'], delay_after=5,expected_color=[ 49 ,195,   0])
        time.sleep(60)
        print(f"✅ [Device: {device}] เล่นเกมจนโหลดข้อมูลเสร็จสมบูรณ์")
        return True
        
    except Exception as e:
        print(f"🔴 [Device: {device}] เกิดข้อผิดพลาดขณะเล่นเกม: {e}")
        return False
    
def login_with_guestID(device,isFirstTime = True):
    """ล็อกอินแบบ Guest โดยแต่ละเครื่องทำงานอิสระ"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"\n🔵 [Device: {device}] เริ่มกระบวนการล็อกอิน (ลองครั้งที่ {retry_count + 1})...")
            time.sleep(10)

            if not isFirstTime:
                restart_game(device)

            # ตรวจสอบหน้าจอเทาก่อนเริ่ม
            if check_pixel_color(device, *CLICK_POSITIONS['is_gray_screen'], [48, 48, 48], tolerance=5):
                print(f"⚠️ [Device: {device}] ตรวจพบจอเทา! จะรีลองใหม่...")
                restart_game(device)
                retry_count += 1
                time.sleep(10)
                continue

            if isFirstTime:
                click_with_delayV2(device, *CLICK_POSITIONS['agree_button'], delay_after=delay, expected_color=[66,66,66])
                click_with_delayV2(device, *CLICK_POSITIONS['allow_button'], delay_after=delay, expected_color=[255,255,255])
                
            # ตรวจสอบจอเทาอีกครั้งหลังคลิก
            if check_pixel_color(device, 674, 417, [48, 48, 48], tolerance=5):
                print(f"⚠️ [Device: {device}] ตรวจพบจอเทาหลังคลิก! จะรีลองใหม่...")
                restart_game(device)
                retry_count += 1
                time.sleep(10)
                continue
            
            # ขั้นตอนที่ 2: ล็อกอินครั้งแรก
            click_with_delayV2(device, *CLICK_POSITIONS['sign_in_apple'], delay_after=10, expected_color=[0,0,0])

            for pos in ['check_box_1', 'check_box_2', 'check_box_3']:
                click_with_delayV2(device, *CLICK_POSITIONS[pos], delay_after=delay, expected_color=[255,255,255])

            click_with_delayV2(device, *CLICK_POSITIONS['agree'], delay_after=delay, expected_color=[202, 241, 202])
            
            press_back_button(device)
            time.sleep(3)

            click_with_delayV2(device, *CLICK_POSITIONS['sign_in_apple'], delay_after=10, expected_color=[0,0,0])
            for pos in ['check_box_1', 'check_box_2', 'check_box_3']:
                click_with_delayV2(device, *CLICK_POSITIONS[pos], delay_after=delay, expected_color=[255,255,255])

            click_with_delayV2(device, *CLICK_POSITIONS['agree'], delay_after=delay, expected_color=[202, 241, 202])
            press_back_button(device)
            time.sleep(3)
            
            # ขั้นตอนที่ 3: ล็อกอินแบบ Guest
            click_with_delayV2(device, *CLICK_POSITIONS['guest_button'], delay_after=10, expected_color=[66, 48, 49])
            click_with_delayV2(device, *CLICK_POSITIONS['login_with_guest'], delay_after=10, expected_color=[250,250, 250])
            for pos in ['check_box_1', 'check_box_2', 'check_box_3']:
                click_with_delayV2(device, *CLICK_POSITIONS[pos], delay_after=delay, expected_color=[255,255,255])

            click_with_delayV2(device, *CLICK_POSITIONS['agree'], delay_after=10, expected_color=[202, 241, 202])
            
            # ขั้นตอนที่ 4: ตั้งค่าหลังล็อกอิน
            click_with_delayV2(device, *CLICK_POSITIONS['first_load_data'], delay_after=delay, expected_color=[ 10, 196,  67])
            click_with_delayV2(device, *CLICK_POSITIONS['ok'], delay_after=30, expected_color=[49, 195, 0])
            click_with_delayV2(device, *CLICK_POSITIONS['create_name'], delay_after=delay, expected_color=[255, 255, 255])
            click_with_delayV2(device, *CLICK_POSITIONS['name_as'], delay_after=delay, expected_color=[ 49,195,0])
            click_with_delayV2(device, *CLICK_POSITIONS['complete_name'], delay_after=delay, expected_color=[49,195,0])
            click_with_delayV2(device, *CLICK_POSITIONS['skip'], delay_after=delay)
            click_with_delayV2(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=delay)
            
            # ตรวจสอบสุดท้ายว่าล็อกอินสำเร็จ
            if not check_pixel_color(device, 674, 417, [48, 48, 48], tolerance=5):
                print(f"🟢 [Device: {device}] ล็อกอินสำเร็จทั้งหมด")
                return True
            else:
                print(f"⚠️ [Device: {device}] ยังพบจอเทาหลังล็อกอิน")
                retry_count += 1
                
        except Exception as e:
            print(f"🔴 [Device: {device}] เกิดข้อพลาด: {e}")
            retry_count += 1
            restart_game(device)
            time.sleep(10)
    
    print(f"❌ [Device: {device}] ล็อกอินล้มเหลวหลังจากลอง {max_retries} ครั้ง")
    return False

def play_tutorial(device):
    """เล่น Tutorial แบบอิสระในแต่ละเครื่อง"""
    try:
        print(f"\n🎮 [Device: {device}] เริ่มเล่น Tutorial...")
        
      
        # 1. ตรวจสอบหน้าจอโหลดเสร็จ
        if not wait_for_load(device, *CLICK_POSITIONS['load_login_completed'], expected_color=[0, 0, 0], timeout=90):
            print(f"🔴 [Device: {device}] ไม่พบหน้าจอ Tutorial")
            return False

        # 2. ขั้นตอนคลิกเริ่มต้น
        for _ in range(4):
            click_with_delayV2(device, *CLICK_POSITIONS['click'], delay_after=2)

        # 3. เลือกตัวละคร
        click_with_delayV2(device, *CLICK_POSITIONS['first_ranger'], delay_after=2,expected_color=[ 16, 158, 239])
        click_with_delayV2(device, *CLICK_POSITIONS['second_ranger'], delay_after=2,expected_color=[255, 255, 255])
        click_with_delayV2(device, *CLICK_POSITIONS['click'], delay_after=4)

        # 4. เก็บทรัพยากร
        for _ in range(3):
            click_with_delayV2(device, *CLICK_POSITIONS['mineral'], delay_after=delay,expected_color=[ 189, 154,  16])

        click_with_delayV2(device, *CLICK_POSITIONS['mineral'], delay_after=delay,expected_color=[ 189, 154,  16])
        click_with_delayV2(device, *CLICK_POSITIONS['click'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['missile_common'], delay_after=2)

        for _ in range(5):
            click_with_delay(device, *CLICK_POSITIONS['missile_common'], delay_after=2)

        # 5. เลือกตัวละครเพิ่ม
        click_with_delayV2(device, *CLICK_POSITIONS['third_ranger'], delay_after=2,expected_color=[255, 195,  90])
        click_with_delayV2(device, *CLICK_POSITIONS['fourth_ranger'], delay_after=2,expected_color=[49, 44, 49])

        # 6. ใช้สกิล
        for _ in range(5):
            click_with_delayV2(device, *CLICK_POSITIONS['missile'], delay_after=2)

        # 7. คลิกต่อเนื่อง
        for _ in range(10):
            click_with_delayV2(device, *CLICK_POSITIONS['click'], delay_after=1)

        # 8. โจมตีศัตรู
        for _ in range(15):
            click_with_delayV2(device, *CLICK_POSITIONS['third_ranger'], delay_after=delay)
            click_with_delayV2(device, *CLICK_POSITIONS['fourth_ranger'], delay_after=delay)

        click_with_delayV2(device, *CLICK_POSITIONS['skip'], delay_after=5)
        click_with_delayV2(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=5)
        print(f"✅ [Device: {device}] เล่น Tutorial เสร็จสิ้น")
        return True

    except Exception as e:
        print(f"🔴 [Device: {device}] เกิดข้อผิดพลาดขณะเล่น Tutorial: {e}")
        return False

def play_until_level_3(device):
  
    for _ in range(3):
        click_with_delay(device, *CLICK_POSITIONS['close_calendar'], delay_after=5)


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
    close_popup(device,1)

def receive_7days(device):
    if not wait_for_load(device, *CLICK_POSITIONS['load_resource_completed'], expected_color=[24, 211, 255], timeout=180):
            print(f"🔴 [Device: {device}] โหลดทรัพยากรล้มเหลว")
            return False
    click_with_delayV2(device, *CLICK_POSITIONS['enter_7days'], delay_after=delay,expected_color=[255, 251, 255])
    click_with_delayV2(device, *CLICK_POSITIONS['receive_7days_ticket'], delay_after=delay,expected_color=[239, 203, 156])
    click_with_delayV2(device, *CLICK_POSITIONS['receive_7days_ticket_success'], delay_after=delay,expected_color=[ 255, 255 , 255])
    click_with_delayV2(device, *CLICK_POSITIONS['close_7days_popup'], delay_after=delay,expected_color=[0, 0, 0])
    click_with_delayV2(device, *CLICK_POSITIONS['open_gift_box'], delay_after=delay,expected_color=[ 33,   8, 165])
    click_with_delayV2(device, *CLICK_POSITIONS['receive_all_btn'], delay_after=delay,expected_color=[ 24, 215, 255])
    click_with_delayV2(device, *CLICK_POSITIONS['receive_all'], delay_after=delay,expected_color= [49, 195, 0])
    click_with_delayV2(device, *CLICK_POSITIONS['receive_all_success'], delay_after=delay,expected_color=[49, 195, 0])

    click_with_delayV2(device, *CLICK_POSITIONS['close_gift_popup'], delay_after=delay,expected_color=[0, 0, 0])

def close_popup(device,flag):
    if flag == 1:
        if not wait_for_load(device, *CLICK_POSITIONS['load_game_with_calendar'], expected_color=[198,227, 247], timeout=180):
                    print(f"🔴 [Device: {device}] ไม่พบหน้า Calendar")
                    return False
    print("เริ่มปิด popup")
    click_with_delay(device, *CLICK_POSITIONS['close_calendar'], delay_after=delay)
    for _ in range(10):
        click_with_delay(device, *CLICK_POSITIONS['receive_ticket'], delay_after=delay)
    for _ in range(15):
        click_with_delay(device, *CLICK_POSITIONS['close_medium_popup'], delay_after=1)
        click_with_delay(device, *CLICK_POSITIONS['click_ticket'], delay_after=1)

    click_with_delayV2(device, *CLICK_POSITIONS['close_largest_popup'], delay_after=delay,expected_color=[11, 42, 96])
    click_with_delayV2(device, *CLICK_POSITIONS['close_show_event'], delay_after=delay,expected_color=[0, 0, 0])

    if flag == 1:
        click_with_delayV2(device, *CLICK_POSITIONS['stage_mode'], delay_after=15,expected_color=[49, 60, 66])
        click_with_delayV2(device, *CLICK_POSITIONS['back_btn'], delay_after=5,)

    click_with_delayV2(device, *CLICK_POSITIONS['close_buff_event'], delay_after=delay,expected_color=[0, 0, 0])

def detect_error_messages(device):
    """Detect specific error messages using OCR and handle them"""
    try:
        img = screencap(device)
        if img is None:
            return False
            
        screenshot_path = f"{device}_error_check.png"
        success = cv2.imwrite(screenshot_path, img)
        if not success:
            log(f"⚠️ {device}: Failed to save screenshot.")
            return False

        # รอให้ระบบเขียนไฟล์เสร็จก่อน
        time.sleep(5)  # อาจปรับเวลาเพิ่มหรือลดได้

        # OCR
        text = pytesseract.image_to_string(Image.open(screenshot_path), lang='eng')
        text = text.lower()

        error_messages = [
            "you must agree to the terms and conditions in order to play the game.",
            "authentication failed. please try again",
            "you must be connected to the internet",
            "unstable network connection do you want to retry?",  # lowercase ให้ตรง
        ]

        for message in error_messages:
            if message in text:
                log(f"⚠️ {device}: Detected error message - '{message}'")
                return True
                
        return False
    except Exception as e:
        log(f"⚠️ {device}: Error detection failed: {str(e)}")
        return False

def is_black_screen(device):
    """ตรวจสอบว่าหน้าจอดำหรือไม่"""
    try:
        img = screencap(device)
        # ตรวจสอบสีที่ตำแหน่งต่างๆ ว่าดำทั้งหมดหรือไม่
        positions = [
            (100, 100), (200, 200), (300, 300), 
            (400, 400), (500, 500), (530, 530)
        ]
        
        for x, y in positions:
            pixel = img[y, x]
            # ถ้าสีไม่ดำ (BGR ไม่ใกล้ 0 ทั้งสามค่า)
            if not (pixel[0] < 10 and pixel[1] < 10 and pixel[2] < 10):
                return False
        return True
    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาดขณะตรวจสอบหน้าจอดำ: {e}")
        return False

def monitor_devices():
    """ตรวจสอบสถานะของอุปกรณ์ทุกๆ 60 วินาที พร้อมตรวจจับ error, จอดำ และ network"""
    global monitoring_active
    log("🔍 เริ่มตรวจสอบอุปกรณ์แบบรวม...")

    while True:
        emulators = get_emulators()
        if not emulators:
            log("⚠️ ไม่พบอุปกรณ์ที่เชื่อมต่อ")
            time.sleep(30)
            continue

        for device in emulators:
            try:
                # ตรวจจับข้อความ error
                if detect_error_messages(device):
                    log(f"⚠️ {device}: พบข้อความผิดพลาด - กำลังรีสตาร์ท")
                    restart_with_clean(device)
                    continue

            except Exception as e:
                log(f"⚠️ {device}: ข้อผิดพลาดระหว่างตรวจสอบ: {str(e)}")

        time.sleep(10)

def check_app_status(device):
    result = subprocess.check_output(f"adb -s {device} shell dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'", shell=True).decode()
    if "com.linecorp.LGRGS" in result:
        print("✅ แอปพลิเคชันกำลังทำงาน")
        return True
    else:
        print("❌ แอปพลิเคชันไม่ทำงาน")
        return False
    
# summon rangers
def check_target_character(device):
    img = screencap(device)
    screenshot_path = f"{device}_check.png"
    cv2.imwrite(screenshot_path, img)

    text = pytesseract.image_to_string(Image.open(screenshot_path), lang='tha+eng')
    print(f"🔍 OCR ตรวจพบข้อความ: {text}")

    for target in target_characters:
        if target.lower() in text.lower():
            print(f"🎉 พบตัวละครเป้าหมาย: {target}")
            return target
        
    return None

def summon_rangers(device, round):
    click_with_delayV2(device, *CLICK_POSITIONS['gacha_btn'], delay_after=5, expected_color=[189, 178, 189])
    global isFound
    # รอให้หน้า gacha โหลดเสร็จ
    if not wait_for_load(device, *CLICK_POSITIONS['load_gacha_page_success'], expected_color=[107, 36, 107], timeout=60):
        print(f"🔴 [Device: {device}] โหลดหน้ากาชาล้มเหลว")
        return False
    

    click_with_delayV2(device, *CLICK_POSITIONS['select_second_gacha'], delay_after=5, expected_color=[132, 36, 140])

    for i in range(round):
        print(f"\n🔁 [Device: {device}] ซัมมอนรอบที่ {i+1}/{round}")
        
        # ทำการซัมมอน
        click_with_delayV2(device, *CLICK_POSITIONS['random_character_gacha'], delay_after=5, expected_color=[222, 255, 255])
        click_with_delayV2(device, *CLICK_POSITIONS['confirm_random_gacha'], delay_after=5, expected_color=[49, 195, 0])
        click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=1)

        # รอให้ animation การซัมมอนเสร็จสิ้น
        time.sleep(5)  # เพิ่มเวลาให้ animation เสร็จ
        
        # ตรวจสอบตัวละครที่ได้รับ
        found_char = None
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries and not found_char:
            print(f"🔄 [Device: {device}] กำลังตรวจสอบตัวละคร (ลองที่ {retry_count+1})")
            found_char = check_target_character(device)
            
            if not found_char:
                retry_count += 1
                time.sleep(3)  # รอสักครู่ก่อนลองใหม่
        
        if found_char:
            log(f"🎯 [Device: {device}] พบตัวละครเป้าหมาย: {found_char} ที่รอบ {i+1}")
            isFound = True
            # เรียกฟังก์ชันเซฟไฟล์
            target_dir = save_directory_path.get()
            if target_dir:
                save_pref_file(device, found_char=found_char, target_dir=target_dir)
            else:
                log("⚠️ ยังไม่ได้เลือกโฟลเดอร์สำหรับเซฟไฟล์")
            
            # ถามผู้ใช้ว่าต้องการซัมมอนต่อหรือไม่
            if messagebox.askyesno("พบตัวละคร", f"พบ {found_char} แล้ว ต้องการซัมมอนต่อหรือไม่?"):
                continue
            else:
                break
        else:
            print(f"🔍 [Device: {device}] ไม่พบตัวละครเป้าหมายในรอบนี้")
        
        # รับตัวละครและเตรียมรอบต่อไป
        click_with_delayV2(device, *CLICK_POSITIONS['receive_character'], delay_after=3)
        time.sleep(2)  # รอสักครู่ก่อนรอบต่อไป

    # กลับไปหน้าหลัก
    click_with_delayV2(device, *CLICK_POSITIONS['back_btn'], delay_after=5)
    log(f"✅ [Device: {device}] เสร็จสิ้นการซัมมอนทั้งหมด")

def save_pref_file(device, found_char=None, target_dir=None):
    try:
        if not target_dir:
            messagebox.showwarning("เลือกโฟลเดอร์ก่อน", "❗ กรุณาเลือกโฟลเดอร์ก่อนเซฟไฟล์")
            return

        android_path = "/data/data/com.linecorp.LGRGS/shared_prefs/_LINE_COCOS_PREF_KEY.xml"
        local_tmp_path = os.path.join(os.getcwd(), "_LINE_COCOS_PREF_KEY.xml")

        # ✅ ROOT ก่อน (บาง emulator ต้องทำก่อนทุกคำสั่ง)
        print("⚙️ กำลังพยายาม root...")
        os.system(f"adb -s {device} root")
        os.system(f"adb -s {device} remount")  # บางกรณีต้อง remount เพื่อให้ writable

        # ✅ ตั้ง permission ด้วย su
        print("⚙️ ตั้ง permission ให้ไฟล์...")
        adb_shell(device, f"su -c 'chmod 777 \"{android_path}\"'")

        # ✅ ดึงไฟล์
        print("📥 ดึงไฟล์...")
        pull_result = os.system(f"adb -s {device} pull \"{android_path}\" \"{local_tmp_path}\"")

        if pull_result != 0 or not os.path.exists(local_tmp_path):
            messagebox.showerror("เกิดข้อผิดพลาด", "❌ ไม่สามารถดึงไฟล์จากเครื่องได้")
            return

        # ✅ สร้างชื่อไฟล์ปลายทาง
        if found_char:
            clean_char_name = ''.join(e for e in found_char if e.isalnum())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_filename = f"{clean_char_name}_{timestamp}_LINE_COCOS_PREF_KEY.xml"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_filename = f"pref_{timestamp}_LINE_COCOS_PREF_KEY.xml"

        target_path = os.path.join(target_dir, target_filename)
        count = 1
        while os.path.exists(target_path):
            if found_char:
                target_filename = f"{clean_char_name}_{count}_LINE_COCOS_PREF_KEY.xml"
            else:
                target_filename = f"pref_{timestamp}_{count}_LINE_COCOS_PREF_KEY.xml"
            target_path = os.path.join(target_dir, target_filename)
            count += 1

        # ✅ ย้ายไฟล์สำเร็จ
        os.replace(local_tmp_path, target_path)
        messagebox.showinfo("สำเร็จ", f"✅ เซฟไฟล์เรียบร้อยที่:\n{target_path}")
        print(f"💾 เซฟไฟล์เรียบร้อย: {target_filename}")

    except Exception as e:
        messagebox.showerror("เกิดข้อผิดพลาด", f"❌ ไม่สามารถเซฟไฟล์ได้: {str(e)}")
        print(f"❌ เกิดข้อผิดพลาดขณะเซฟไฟล์: {e}")

# click && swipe
def click_with_delayV2(device, x, y, delay_after=1, expected_color=None, timeout=180):
    try:
        if expected_color is not None:
            if not wait_for_load(device, x, y, expected_color, timeout):
                print(f"❌ คลิกไม่สำเร็จที่ ({x}, {y}) - สีไม่ตรง")
                return False
        
        click(device, x, y)
        time.sleep(delay_after)
        return True
    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาดขณะคลิก: {str(e)}")
        return False

def click(device, x, y):
    log(f"🎯 กำลังคลิกที่ตำแหน่ง{x} {y} บนอุปกรณ์ {device}")
    adb_shell(device, f"input tap {x} {y}")
    
def click_with_delay(device, x, y, delay_after=1):
    print(f"🖱️ [Device: {device}] คลิกที่ ({x}, {y}) - รอ {delay_after} วินาที")
    click(device, x, y)  # เพิ่มคำสั่งคลิกจริง
    time.sleep(delay_after)    

def swipe_screen(device, start_x, start_y, end_x, end_y, duration=1000):
    print(f"🖱️ ลากหน้าจอจาก ({start_x}, {start_y}) ไปยัง ({end_x}, {end_y}) ใช้เวลา {duration} ms")
    adb_shell(device, f"input swipe {start_x} {start_y} {end_x} {end_y} {duration}")
    time.sleep(1)  # รอให้การลากเสร็จ

  
def press_back_button(device):
    print(f"🔙 กดปุ่มกลับบน {device}")
    adb_shell(device, "input keyevent 4")  # คำสั่งสำหรับกดปุ่มกลับ
    time.sleep(1)  # รอให้คำสั่งสำเร็จ

def screencap(device):
    cap1 = subprocess.check_output(f'adb -s {device} exec-out screencap -p', shell=True)
    image = np.frombuffer(cap1, dtype=np.uint8)
    img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return img

# check
def wait_for_event(device, condition_func, timeout=60, interval=1, *args, **kwargs):
    """
    รอจนกว่า condition_func จะคืนค่า True
    *args และ **kwargs จะถูกส่งต่อให้ condition_func
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func(device, *args, **kwargs):
            return True
        time.sleep(interval)
    return False

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

def check_pixel_color(device, x, y, expected_color, tolerance=10):
    """
    ตรวจสอบสีที่ตำแหน่ง (x,y)
    expected_color: (B, G, R)
    tolerance: ค่าความคลาดเคลื่อนที่ยอมรับได้
    """
    img = screencap(device)
    pixel = img[y, x]
    
    return abs(int(pixel[0]) - int(expected_color[0])) <= tolerance and \
           abs(int(pixel[1]) - int(expected_color[1])) <= tolerance and \
           abs(int(pixel[2]) - int(expected_color[2])) <= tolerance

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

# restart
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

def restart_with_clean(device):
    """Restart game with complete data cleaning"""
    try:
        log(f"🔄 {device}: Performing clean restart...")
        
        # 1. Force stop the game
        adb_shell(device, "am force-stop com.linecorp.LGRGS")
        time.sleep(2)
        
        # 2. Clear all game data
        adb_shell(device, "pm clear com.linecorp.LGRGS")
        time.sleep(3)
        
        # 3. Restart the game
        adb_shell(device, "monkey -p com.linecorp.LGRGS -c android.intent.category.LAUNCHER 1")
        time.sleep(15)
        
        # 4. Verify restart
        if check_app_status(device):
            log(f"✅ {device}: Clean restart successful")
            re_id(device,isFirstTime=True)
            return True
            
        log(f"❌ {device}: Clean restart failed")
        return False
    except Exception as e:
        log(f"❌ {device}: Clean restart error: {str(e)}")
        return False

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

# debug
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

## Gui Function
def log(msg):
    output_text.config(state='normal')
    output_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {msg}\n")
    output_text.see(tk.END)
    output_text.config(state='disabled')

def start_bot_thread():
    thread = threading.Thread(target=start_bot, daemon=True)
    thread.start()

def start_bot():
    global running, monitoring_active, isFound
    running = True
    monitoring_active = True
    isFound = False  # รีเซ็ตค่าการพบตัวละคร
    log("เริ่มทำงานบอท...")
    run_all_independent()

def stop_bot():
    global running, monitoring_active
    running = False
    monitoring_active = False  # หยุดการ monitor ด้วย
    log("หยุดการทำงานของบอทแล้ว")
    time.sleep(2)  # รอให้ thread อื่นๆ หยุดทำงาน



def toggle_resource():
    global isLoadResource
    isLoadResource = not load_resource_var.get()
    log(f"🔄 Load Resource: {not isLoadResource}")

def toggle_7days():
    """Toggle 7-day rewards"""
    global skip_7days
    skip_7days = not skip_7days_var.get()
    log(f"🔄 7-day rewards set to: {not skip_7days}")

def toggle_random_summon():
    """Toggle random summon"""
    global random_summon
    random_summon = random_summon_var.get()
    log(f"🔄 Random summon set to: {random_summon}")

def calculate_summon_times():
    global summon_times
    try:
        text = ticket_input.get()
        ticket_count = int(text) if text else 0
        summon_times = ticket_count // 5
        log(f"🎟 คำนวณจำนวนครั้งในการซัมมอน: {summon_times} (จาก {ticket_count} ตั๋ว)")
    except ValueError:
        log("❌ กรุณาใส่เลขจำนวนเต็มของตั๋ว")
        summon_times = 0

def choose_save_directory():
    path = filedialog.askdirectory(title="📁 เลือกโฟลเดอร์สำหรับเซฟ PREF KEY")
    if path:
        save_directory_path.set(path)
        messagebox.showinfo("เลือกสำเร็จ", f"📂 จะเซฟไฟล์ไว้ที่:\n{path}")
    else:
        messagebox.showinfo("ยกเลิก", "❗ ยังไม่ได้เลือกโฟลเดอร์")

def add_error_handling_gui():
    error_frame = ttk.LabelFrame(main_frame, text="🛑 Error Handling", padding=10)
    error_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=5)
    
    ttk.Label(error_frame, 
             text="Automatically handles:\n"
                 "- Terms agreement errors\n"
                 "- Authentication failures\n"
                 "- Internet connection errors").pack()

def update_target_characters():
    global target_characters
    input_text = target_entry.get()
    if input_text:
        # แยกชื่อตัวละครด้วยคอมม่า และลบช่องว่าง
        target_characters = [name.strip().upper() for name in input_text.split(",") if name.strip()]
        log(f"🔄 อัปเดตตัวละครเป้าหมาย: {', '.join(target_characters)}")
    else:
        log("⚠️ กรุณากรอกชื่อตัวละครเป้าหมาย")

def show_help():
    """Show help message"""
    help_text = """
    ✨ Theprachaball Bot Help ✨
    
    1. Connect your emulators via ADB
    2. Configure settings:
       - Ticket count: Number of gacha tickets available
       - Target characters: Comma-separated list of characters to look for
       - Excluded devices: Comma-separated list of emulators to exclude
    3. Toggle options as needed:
       - Load resources: Whether to load game resources
       - 7-day rewards: Whether to collect 7-day login rewards
       - Random summon: Whether to perform random summons
       - Tutorial mode: Whether to play through tutorial
    4. Select a save directory for PREF KEY files
    5. Click "Start Bot" to begin
    
    Troubleshooting:
    - If the bot gets stuck, check the log for errors
    - Make sure ADB is properly configured
    - Ensure emulators are visible in 'adb devices'
    - For gray/black screens, try restarting the emulator
    
    Hotkeys:
    - F1: Show this help
    - Ctrl+Q: Quit application
    """
    
    messagebox.showinfo("Help", help_text)

def update_excluded_devices():
    """Update excluded devices list"""
    global excluded_devices
    input_text = excluded_devices_entry.get()
    if input_text:
        excluded_devices = [device.strip() for device in input_text.split(",") if device.strip()]
        log(f"🚫 Excluded devices updated: {', '.join(excluded_devices)}")
    else:
        excluded_devices = []
        log("🔄 No devices excluded")

def toggle_monitoring():
    global monitoring_active
    monitoring_active = monitoring_var.get()
    log(f"📡 Monitoring {'เปิด' if monitoring_active else 'ปิด'}")

    
def update_global_delay(*args):
    global delay
    try:
        delay = int(delay_var.get())
        log(f"⏱️ อัปเดต Delay: {delay} วินาที")
    except ValueError:
        log("❌ Delay ต้องเป็นตัวเลขจำนวนเต็ม")

# ===== สร้าง GUI =====
root = tk.Tk()
root.title("✨ Theprachaball Bot Controller ✨")
root.geometry("800x900")
root.configure(bg="#f0f4f8")

# Variables
save_directory_path = tk.StringVar()
delay_var = tk.StringVar()
load_resource_var = tk.BooleanVar(value=True)
skip_7days_var = tk.BooleanVar(value=True)
random_summon_var = tk.BooleanVar(value=True)
tutorial_mode_var = tk.BooleanVar(value=True)
monitoring_var = tk.BooleanVar(value=True)
delay_var.set(5)  # default value

# Fonts
default_font = tkfont.Font(family="Segoe UI", size=11)
heading_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")

# Styles
style = ttk.Style()
style.theme_use("clam")

style.configure("TButton",
    font=default_font,
    padding=6,
    relief="flat",
    background="#4CAF50",
    foreground="white"
)
style.map("TButton",
    background=[("active", "#45a049"), ("disabled", "#a5d6a7")]
)

style.configure("TCheckbutton",
    background="#f0f4f8",
    font=default_font
)

style.configure("TLabel",
    background="#f0f4f8",
    font=default_font
)

# Main layout
main_frame = ttk.Frame(root)
main_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Header
header_label = ttk.Label(main_frame, text="🎮 Theprachaball Bot Control Panel", font=heading_font, foreground="#2c3e50")
header_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

# Control buttons
control_frame = ttk.Frame(main_frame)
control_frame.grid(row=1, column=0, columnspan=3, pady=5)

start_btn = ttk.Button(control_frame, text="▶ เริ่มบอท", command=start_bot_thread)
start_btn.grid(row=0, column=0, padx=5)

stop_btn = ttk.Button(control_frame, text="⏹ หยุดบอท", command=stop_bot)
stop_btn.grid(row=0, column=1, padx=5)

help_btn = ttk.Button(control_frame, text="❓ คู่มือการใช้งาน", command=show_help)
help_btn.grid(row=0, column=2, padx=5)

# Settings frame
settings_frame = ttk.LabelFrame(main_frame, text="⚙️ ตั้งค่า", padding=10)
settings_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)

# Resource loading
load_resource_cb = ttk.Checkbutton(settings_frame, text="โหลดทรัพยากรหรือไม่", variable=load_resource_var, command=toggle_resource)
load_resource_cb.grid(row=0, column=0, sticky="w", pady=2)

# 7-day rewards
skip_7days_cb = ttk.Checkbutton(settings_frame, text="รับตั๋ว 7 วันหรือไม่", variable=skip_7days_var, command=toggle_7days)
skip_7days_cb.grid(row=1, column=0, sticky="w", pady=2)

# Random summon
random_summon_cb = ttk.Checkbutton(settings_frame, text="สุ่มอัตโนมัติหรือไม่", variable=random_summon_var, command=toggle_random_summon)
random_summon_cb.grid(row=2, column=0, sticky="w", pady=2)

# Ticket input
ticket_frame = ttk.Frame(settings_frame)
ticket_frame.grid(row=4, column=0, sticky="w", pady=5)

ticket_label = ttk.Label(ticket_frame, text="🎫 ตั๋ว:")
ticket_label.grid(row=0, column=0, padx=(0, 5))

ticket_input = ttk.Entry(ticket_frame, font=default_font, width=10)
ticket_input.grid(row=0, column=1)
ticket_input.insert(0, "0")
ticket_input.bind("<KeyRelease>", lambda event: calculate_summon_times())

# Target characters
target_frame = ttk.Frame(settings_frame)
target_frame.grid(row=5, column=0, sticky="w", pady=5)

target_label = ttk.Label(target_frame, text="🎯 ตัวละครที่ต้องการหา:")
target_label.grid(row=0, column=0, padx=(0, 5))

target_entry = ttk.Entry(target_frame, font=default_font, width=30)
target_entry.grid(row=0, column=1, padx=(0, 5))
target_entry.insert(0, "SENKU")

update_target_btn = ttk.Button(target_frame, text="อัพเดต", command=update_target_characters)
update_target_btn.grid(row=0, column=2)

# Excluded devices
excluded_frame = ttk.Frame(settings_frame)
excluded_frame.grid(row=6, column=0, sticky="w", pady=5)

excluded_label = ttk.Label(excluded_frame, text="🚫 จอที่จะไม่บอท:")
excluded_label.grid(row=0, column=0, padx=(0, 5))

excluded_devices_entry = ttk.Entry(excluded_frame, font=default_font, width=30)
excluded_devices_entry.grid(row=0, column=1, padx=(0, 5))

update_excluded_btn = ttk.Button(excluded_frame, text="อัพเดต", command=update_excluded_devices)
update_excluded_btn.grid(row=0, column=2)

delay_frame = ttk.Frame(settings_frame)
delay_frame.grid(row=3, column=1, sticky="w", pady=5, padx=10)

delay_label = ttk.Label(delay_frame, text="⏱️ เดเลย์ (วินาที):")
delay_label.grid(row=0, column=0, padx=(0, 5))

delay_entry = ttk.Entry(delay_frame, font=default_font, width=10, textvariable=delay_var, justify="center")
delay_entry.grid(row=0, column=1)
delay_var.trace_add("write", update_global_delay)

# Save directory
save_dir_frame = ttk.Frame(main_frame)
save_dir_frame.grid(row=3, column=0, columnspan=3, pady=5)

choose_dir_btn = ttk.Button(save_dir_frame, text="📂 เลือกโฟลเดอร์ที่ต้องการเซฟ", command=choose_save_directory)
choose_dir_btn.grid(row=0, column=0, padx=5)

chosen_dir_label = ttk.Label(save_dir_frame, textvariable=save_directory_path, foreground="gray", wraplength=400)
chosen_dir_label.grid(row=1, column=0, pady=(0, 10))

# Log output
log_frame = ttk.LabelFrame(main_frame, text="📋 Log", padding=10)
log_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=5)


output_text = scrolledtext.ScrolledText(log_frame, height=20, font=("Consolas", 10), state='disabled', background="#ecf0f1")
output_text.pack(fill='both', expand=True)

# Configure grid weights
main_frame.grid_rowconfigure(4, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Key bindings
root.bind("<F1>", lambda event: show_help())
root.bind("<Control-q>", lambda event: root.quit())

# Start monitoring thread
monitor_thread = threading.Thread(target=monitor_devices, daemon=True)
monitor_thread.start()

monitoring_cb = ttk.Checkbutton(
    settings_frame,
    text="ดักข้อผิดพลาดระหว่างบอท",
    variable=monitoring_var,
    command=toggle_monitoring
)
monitoring_cb.grid(row=3, column=0, sticky="w", pady=2)
# Main loop
root.mainloop()