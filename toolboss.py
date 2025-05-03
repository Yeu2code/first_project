import customtkinter as ctk
import threading
import time
import pyautogui
import random
import keyboard
from tkinter import messagebox
import json
import os

# ===================== CÀI ĐẶT GIAO DIỆN =====================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class AutoClicker:
    def __init__(self):
        self.stop_flag = threading.Event()
        self.operation_count = 0
        self.config_file = "config.json"
        self.default_config = {
            'shop_button': (1075, 290),
            'item_slot': (804, 365),
            'confirm_button': (581, 434),
            'key_sequence': ['1', '2', '4', 'e'],
            'key_delays': 0.1,
            'space_duration': 0.5,
            'loop_delay': 1.0,
            'start_delay': 2.2,  # Thời gian chờ trước khi bắt đầu (giây)
        }
        self.load_config()
        
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
                self.config['shop_button'] = tuple(self.config['shop_button'])
                self.config['item_slot'] = tuple(self.config['item_slot'])
                self.config['confirm_button'] = tuple(self.config['confirm_button'])
        else:
            self.config = self.default_config
            
    def save_config(self):
        with open(self.config_file, 'w') as f:
            temp_config = self.config.copy()
            temp_config['shop_button'] = list(temp_config['shop_button'])
            temp_config['item_slot'] = list(temp_config['item_slot'])
            temp_config['confirm_button'] = list(temp_config['confirm_button'])
            json.dump(temp_config, f, indent=4)
            
    def safe_click(self, position):
        try:
            pyautogui.click(position)
            time.sleep(random.uniform(0.3, 0.7))
            return True
        except Exception as e:
            print(f"Click failed: {e}")
            return False
            
    def press_keys(self):
        try:
            # Nhấn từng phím theo thứ tự với độ trễ
            for key in self.config['key_sequence']:
                keyboard.press(key)
                time.sleep(self.config['key_delays'])  # Giữ phím trong khoảng thời gian này
                keyboard.release(key)
                time.sleep(0.1)  # Thêm một chút delay giữa các phím
                
            # Giữ phím space
            keyboard.press(' ')
            time.sleep(self.config['space_duration'])
            keyboard.release(' ')
            
        except Exception as e:
            print(f"Lỗi khi nhấn phím: {e}")
        
    def run_buy_items(self, callback):
        self.stop_flag.clear()
        self.operation_count = 0
        
        while not self.stop_flag.is_set():
            try:
                if not all([
                    self.safe_click(self.config['shop_button']),
                    self.safe_click(self.config['item_slot']),
                    self.safe_click(self.config['confirm_button'])
                ]):
                    continue
                    
                self.operation_count += 1
                callback(f"Đang mua vật phẩm: {self.operation_count}")
                time.sleep(self.config['loop_delay'])
                
            except Exception as e:
                callback(f"Lỗi: {str(e)}")
                break
                
    def run_attack(self, callback):
        self.stop_flag.clear()
        self.operation_count = 0
         # Thêm delay trước khi bắt đầu
        time.sleep(self.config['start_delay'])
        callback(f"Đang chờ {self.config['start_delay']} giây trước khi bắt đầu...")
        while not self.stop_flag.is_set():
            try:
                start_time = time.time()
                self.press_keys()
                elapsed_time = time.time() - start_time
                
                self.operation_count += 1
                callback(f"Đang tấn công: {self.operation_count} | Thời gian: {elapsed_time:.2f}s")
                time.sleep(max(0, self.config['loop_delay'] - elapsed_time))  # Đảm bảo tổng thời gian mỗi lần lặp là loop_delay
            except Exception as e:
                callback(f"Lỗi: {str(e)}")
                break
                
    def stop(self):
        self.stop_flag.set()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌟 Auto Clicker Pro - Gunny Tool")
        self.geometry("800x600")
        self.clicker = AutoClicker()
        self.setup_ui()
        
    def setup_ui(self):
        # Main container với scroll
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tạo các tab
        self.tabview = ctk.CTkTabview(self.main_frame, width=750, height=450)
        self.tabview.pack(pady=10)
        
        # Tab Click chuột
        self.tab1 = self.tabview.add("Mua vật phẩm")
        self.setup_click_tab()
        
        # Tab Bàn phím
        self.tab2 = self.tabview.add("Tấn công")
        self.setup_keyboard_tab()
        
        # Tab Cài đặt
        self.tab3 = self.tabview.add("Cài đặt")
        self.setup_settings_tab()
        
        # Thanh trạng thái
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.pack(pady=10, fill="x")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="🟢 Sẵn sàng",
            font=("Arial", 14, "bold")
        )
        self.status_label.pack(side="left", padx=10)
        
        self.counter_label = ctk.CTkLabel(
            self.status_frame, 
            text="Số lần: 0 | Thời gian: 0.00s",
            font=("Arial", 12)
        )
        self.counter_label.pack(side="right", padx=10)
        
        # Nút điều khiển - Đặt ở dưới cùng
        self.control_frame = ctk.CTkFrame(self.main_frame)
        self.control_frame.pack(pady=(0,10), fill="x")
        
        self.buy_btn = ctk.CTkButton(
            self.control_frame,
            text="🛒 MUA VẬT PHẨM",
            command=lambda: self.start_operation("buy"),
            fg_color="#4CAF50",
            font=("Arial", 12, "bold"),
            width=180
        )
        self.buy_btn.pack(side="left", padx=5)
        
        self.attack_btn = ctk.CTkButton(
            self.control_frame,
            text="🔫 TẤN CÔNG",
            command=lambda: self.start_operation("attack"),
            fg_color="#2196F3",
            font=("Arial", 12, "bold"),
            width=180
        )
        self.attack_btn.pack(side="left", padx=5)
        
        self.stop_btn = ctk.CTkButton(
            self.control_frame,
            text="⛔ DỪNG",
            command=self.stop_operation,
            fg_color="#f44336",
            font=("Arial", 12, "bold"),
            width=180,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)
        
        # Phím tắt
        keyboard.add_hotkey('esc', self.stop_operation)
        
    def setup_click_tab(self):
        coord_frame = ctk.CTkFrame(self.tab1)
        coord_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(coord_frame, text="CÀI ĐẶT MUA VẬT PHẨM", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Tọa độ các nút
        coord_fields = [
            ("Nút cửa hàng (X,Y):", "shop_button"),
            ("Ô vật phẩm (X,Y):", "item_slot"),
            ("Nút xác nhận (X,Y):", "confirm_button")
        ]
        
        self.coord_entries = {}
        for label, key in coord_fields:
            ctk.CTkLabel(coord_frame, text=label).pack()
            entry = ctk.CTkEntry(coord_frame)
            entry.pack()
            entry.insert(0, f"{self.clicker.config[key][0]},{self.clicker.config[key][1]}")
            self.coord_entries[key] = entry
        
        ctk.CTkButton(
            coord_frame,
            text="📌 Lấy tọa độ",
            command=self.get_current_pos,
            width=150
        ).pack(pady=10)
        
    def setup_keyboard_tab(self):
        key_frame = ctk.CTkFrame(self.tab2)
        key_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(key_frame, text="CÀI ĐẶT TẤN CÔNG", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Các trường cài đặt
        settings = [
            ("Chuỗi phím (cách nhau bằng dấu phẩy):", "key_sequence", ",".join(self.clicker.config['key_sequence'])),
            ("Thời gian giữ mỗi phím (giây):", "key_delays", str(self.clicker.config['key_delays'])),
            ("Thời gian giữ phím Space (giây):", "space_duration", str(self.clicker.config['space_duration'])),
            ("Thời gian nghỉ giữa các lần (giây):", "loop_delay", str(self.clicker.config['loop_delay']))
        ]
        
        self.key_entries = {}
        for label, key, default in settings:
            ctk.CTkLabel(key_frame, text=label).pack()
            entry = ctk.CTkEntry(key_frame)
            entry.pack()
            entry.insert(0, default)
            self.key_entries[key] = entry
            
    def setup_settings_tab(self):
        settings_frame = ctk.CTkFrame(self.tab3)
        settings_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(settings_frame, text="CÀI ĐẶT CHUNG", font=("Arial", 14, "bold")).pack(pady=5)
        
        ctk.CTkButton(
            settings_frame,
            text="💾 Lưu cấu hình",
            command=self.save_settings,
            width=150
        ).pack(pady=10)
        
        help_text = """
        HƯỚNG DẪN:
        1. Chọn tab chức năng cần dùng
        2. Cài đặt thông số
        3. Nhấn nút tương ứng để chạy
        4. Nhấn DỪNG hoặc ESC để dừng
        
        Chức năng riêng lẻ:
        - Mua vật phẩm: Chỉ thao tác chuột
        - Tấn công: Chỉ thao tác bàn phím
        
        THÔNG SỐ TẤN CÔNG:
        - Chuỗi phím: Nhập các phím cách nhau dấu phẩy (1,2,4,e)
        - Thời gian giữ phím: Thời gian giữ mỗi phím (giây)
        - Thời gian Space: Thời gian giữ phím space
        - Thời gian nghỉ: Thời gian chờ giữa các lần thực hiện
        """
        ctk.CTkLabel(settings_frame, text=help_text, justify="left").pack(pady=10)
        
    def get_current_pos(self):
        messagebox.showinfo("Lấy tọa độ", "Di chuột đến vị trí cần lấy tọa độ trong 5 giây...")
        time.sleep(5)
        x, y = pyautogui.position()
        messagebox.showinfo("Tọa độ hiện tại", f"X: {x}, Y: {y}")
        
    def parse_coordinates(self, coord_str):
        try:
            return tuple(map(int, coord_str.split(',')))
        except:
            messagebox.showerror("Lỗi", "Tọa độ không hợp lệ!")
            return None
            
    def save_settings(self):
        try:
            # Lưu tọa độ
            for key, entry in self.coord_entries.items():
                if coords := self.parse_coordinates(entry.get()):
                    self.clicker.config[key] = coords
            
            # Lưu cài đặt bàn phím
            self.clicker.config['key_sequence'] = [
                k.strip() for k in self.key_entries['key_sequence'].get().split(',')
            ]
            self.clicker.config['key_delays'] = float(self.key_entries['key_delays'].get())
            self.clicker.config['space_duration'] = float(self.key_entries['space_duration'].get())
            self.clicker.config['loop_delay'] = float(self.key_entries['loop_delay'].get())
            
            self.clicker.save_config()
            messagebox.showinfo("Thành công", "Đã lưu cấu hình!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi lưu: {str(e)}")
            
    def update_status(self, message):
        if ":" in message:  # Cập nhật số lần
            action, count = message.split(":", 1)
            self.counter_label.configure(text=f"{action}: {count.strip()}")
        else:  # Thông báo lỗi
            self.status_label.configure(text=f"🔴 {message}")
            
    def start_operation(self, mode):
        self.save_settings()
        
        self.status_label.configure(text="🟡 Đang chạy...", text_color="orange")
        self.buy_btn.configure(state="disabled")
        self.attack_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        if mode == "buy":
            target_func = self.clicker.run_buy_items
        else:
            target_func = self.clicker.run_attack
            
        threading.Thread(
            target=target_func,
            args=(self.update_status,),
            daemon=True
        ).start()
        
    def stop_operation(self):
        self.clicker.stop()
        self.status_label.configure(text="🟢 Đã dừng", text_color="green")
        self.buy_btn.configure(state="normal")
        self.attack_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
    def __del__(self):
        keyboard.remove_hotkey('esc')

if __name__ == "__main__":
    app = App()
    app.mainloop()