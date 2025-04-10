import subprocess
import time
import numpy as np
import cv2
from datetime import datetime
import threading

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
    'start_stage'   :  (480, 476),
    'select_meteor' : (185, 359),
    'use_meteor' : (46, 46),
    'receive_level' : (475, 454),
    'gacha_btn' : (662, 115),
    'random' : (360, 450),
    'receive_character': (396, 440),
    'select_team': (187, 473),
    'team_save_btn': (550, 359),
    'load_resource': (475, 360),
    'load_additional_resource': (554, 385),
    'close_large_popup': (816, 60),
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
    'load_tutorial_completed'  : (14, 526)

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
# ✅ กดปุ่ม "กลับ" (Back)

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
        click_with_delay(device, *CLICK_POSITIONS['skip'], delay_after=2)
        click_with_delay(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=10)
        
        # ขั้นตอนที่ 2: เลือกโหมดและสเตจ
        click_with_delay(device, *CLICK_POSITIONS['stage_mode'], delay_after=10)
        click_with_delay(device, *CLICK_POSITIONS['select_stage_1'], delay_after=10)
        
        # ขั้นตอนที่ 3: คลิกเตรียมตัว
        for _ in range(5):
            click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=2)
        time.sleep(10)
        
        # ขั้นตอนที่ 4: เริ่มสเตจ
        click_with_delay(device, *CLICK_POSITIONS['start_stage'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['select_meteor'], delay_after=10)
        click_with_delay(device, *CLICK_POSITIONS['first_ranger'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['use_meteor'], delay_after=5)
        
        # ขั้นตอนที่ 5: โจมตีศัตรู
        for _ in range(10):
            click_with_delay(device, *CLICK_POSITIONS['first_ranger'], delay_after=2)
            click_with_delay(device, *CLICK_POSITIONS['second_ranger'], delay_after=2)
            click_with_delay(device, *CLICK_POSITIONS['third_ranger'], delay_after=2)
            click_with_delay(device, *CLICK_POSITIONS['fourth_ranger'], delay_after=2)
        
        # ขั้นตอนที่ 6: รับรางวัล
        click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['receive_level'], delay_after=5)
        
        for _ in range(4):
            click_with_delay(device, *CLICK_POSITIONS['click'], delay_after=2)
        
        # ขั้นตอนที่ 7: ระบบกาชา
        click_with_delay(device, *CLICK_POSITIONS['skip'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['start_btn_skip'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['gacha_btn'], delay_after=10)
        click_with_delay(device, *CLICK_POSITIONS['random'], delay_after=10)
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
        click_with_delay(device, *CLICK_POSITIONS['agree_button'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['allow_button'], delay_after=5)
        
        # ขั้นตอนที่ 2: ล็อกอินครั้งแรก
        click_with_delay(device, *CLICK_POSITIONS['sign_in_apple'], delay_after=5)
        for pos in ['check_box_1', 'check_box_2', 'check_box_3']:
            click_with_delay(device, *CLICK_POSITIONS[pos], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['agree'], delay_after=5)
        
        # ย้อนกลับและลองใหม่
        press_back_button(device)
        time.sleep(3)
        click_with_delay(device, *CLICK_POSITIONS['sign_in_apple'], delay_after=5)
        for pos in ['check_box_1', 'check_box_2', 'check_box_3']:
            click_with_delay(device, *CLICK_POSITIONS[pos], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['agree'], delay_after=5)
        press_back_button(device)
        time.sleep(3)
        
        # ขั้นตอนที่ 3: ล็อกอินแบบ Guest
        click_with_delay(device, *CLICK_POSITIONS['guest_button'], delay_after=5)
        click_with_delay(device, *CLICK_POSITIONS['login_with_guest'], delay_after=5)
        for pos in ['check_box_1', 'check_box_2', 'check_box_3']:
            click_with_delay(device, *CLICK_POSITIONS[pos], delay_after=5)
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
        time.sleep(30)
        return True

    except Exception as e:
        print(f"🔴 [Device: {device}] เกิดข้อผิดพลาดขณะเล่น Tutorial: {e}")
        return False

def re_id(device):
    try:
        package = "com.linecorp.LGRGS"
        print(f"🧹 ล้างข้อมูล {device}")
        adb_shell(device, f"pm clear {package}")
        time.sleep(2)

        print(f"🚀 เปิดเกม {device}")
        adb_shell(device, f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
        time.sleep(10)
        print(f"🚀 เริ่มรีไอดี {device}")

        login_with_guestID(device)
        play_tutorial(device)
        play_until_load_data(device)
        delete_account(device)
        
        # บันทึกภาพหน้าจอ
        img = screencap(device)
        cv2.imwrite(f"{device}_screenshot.jpg", img)
        print(f"✅ รีไอดีเสร็จ {device}")
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


# ✅ ฟังก์ชันสำหรับลากหน้าจอ
def swipe_screen(device, start_x, start_y, end_x, end_y, duration=1000):
    print(f"🖱️ ลากหน้าจอจาก ({start_x}, {start_y}) ไปยัง ({end_x}, {end_y}) ใช้เวลา {duration} ms")
    adb_shell(device, f"input swipe {start_x} {start_y} {end_x} {end_y} {duration}")
    time.sleep(1)  # รอให้การลากเสร็จ

def monitor_app_loop(interval_sec=90):
    print("📡 เริ่มการตรวจสอบแอปทุกๆ", interval_sec, "วินาที")
    while True:
        emulators = get_emulators()
        for device in emulators:
            print(f"🔍 ตรวจสอบแอปบน {device}")
            if not check_app_status(device):
                print(f"🔁 รีสตาร์ทแอป {device} ด้วย run_all()")
                run_all()
        time.sleep(interval_sec)

def run_all_independent():
    """รันแต่ละเครื่องแบบอิสระ ไม่ต้องรอพร้อมกัน"""
    emulators = get_emulators()
    if not emulators:
        print("❌ ไม่พบ Emulator ที่เปิดอยู่")
        return
    
    threads = []
    for device in emulators:
        thread = threading.Thread(
            target=process_device_independent, 
            args=(device,),
            name=f"Thread-{device}"
        )
        threads.append(thread)
        thread.start()
        time.sleep(1)  # เว้นระยะเริ่มต้นแต่ละเครื่องเล็กน้อย
    
    print(f"🚀 เริ่มทำงานบน {len(emulators)} เครื่อง...")

def process_device_independent(device):
    """กระบวนการสำหรับแต่ละเครื่องแบบอิสระ"""
    try:
        print(f"\n⚙️ [Device: {device}] เริ่มทำงาน...")
        re_id(device)
    except Exception as e:
        print(f"❌ [Device: {device}] เกิดข้อผิดพลาด: {e}")
if __name__ == "__main__":
    print("=== LRG Auto Re-ID Bot ===")
    print("1. รันแบบอิสระ (ไม่ต้องรอพร้อมกัน)")
    print("2. Debug ค่า Pixel")
    choice = input("เลือกโหมด: ")
    
    if choice == "1":
        while True:
            run_all_independent()  # ใช้ฟังก์ชันใหม่ที่ทำงานอิสระ
            print("\n🕓 รอ 90 วินาทีก่อนรอบต่อไป...")
            time.sleep(90)
    elif choice == "2":
        emulators = get_emulators()
        if not emulators:
            print("ไม่พบ Emulator ที่เปิดอยู่")
        else:
            print(f"เลือก Emulator เพื่อ Debug:")
            for i, emu in enumerate(emulators, 1):
                print(f"{i}. {emu}")
            emu_choice = int(input("เลือกหมายเลข: ")) - 1
            debug_pixel(emulators[emu_choice])
    elif choice == "3":
        print("ตำแหน่งคลิกปัจจุบัน:")
        for name, pos in CLICK_POSITIONS.items():
            print(f"{name}: {pos}")