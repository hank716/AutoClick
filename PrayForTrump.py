import tkinter as tk
from tkinter import messagebox
import threading
import time
import keyboard
import pydirectinput
import random

pydirectinput.FAILSAFE = True

class GameAutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("PrayForTrump - Made by Hank")
        self.root.geometry("450x720") 
        self.root.resizable(False, False)

        self.is_running = False
        self.is_recording = False
        self.key_list = []

        # --- 介面佈局 ---
        tk.Label(root, text="【 錄製按鍵序列 】", font=("Microsoft JhengHei", 10, "bold")).pack(pady=5)
        self.key_display = tk.Text(root, height=4, width=55, state='disabled', bg="#f8f9fa", font=("Consolas", 9))
        self.key_display.pack(pady=5, padx=10)
        
        rec_frame = tk.Frame(root)
        rec_frame.pack()
        self.record_btn = tk.Button(rec_frame, text="開始錄製", command=self.toggle_record, bg="#ADD8E6", width=12)
        self.record_btn.pack(side=tk.LEFT, padx=5)
        self.clear_btn = tk.Button(rec_frame, text="清空按鍵", command=self.clear_keys, width=12)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # --- 設定區 ---
        time_frame = tk.LabelFrame(root, text=" 獨立隨機化設定 ", padx=10, pady=10)
        time_frame.pack(pady=10, padx=10, fill="x")

        # 1. 按鍵間延遲設定
        tk.Label(time_frame, text="基礎按鍵延遲 (s):").grid(row=0, column=0, sticky="w")
        self.key_int_var = tk.StringVar(value="0.2")
        self.key_int_var.trace_add("write", lambda *args: self.update_preview())
        tk.Entry(time_frame, textvariable=self.key_int_var, width=8).grid(row=0, column=1, padx=5, sticky="w")

        tk.Label(time_frame, text="按鍵隨機率 (±%):", fg="#5bc0de").grid(row=1, column=0, sticky="w")
        self.key_rand_scale = tk.Scale(time_frame, from_=0, to=1000, orient=tk.HORIZONTAL, command=lambda x: self.update_preview())
        self.key_rand_scale.set(20)
        self.key_rand_scale.grid(row=1, column=1, sticky="we")

        # 分隔線
        tk.Canvas(time_frame, height=2, bg="#ddd", highlightthickness=0).grid(row=2, columnspan=2, sticky="we", pady=10)

        # 2. 輪詢間延遲設定
        tk.Label(time_frame, text="基礎整輪休息 (s):").grid(row=3, column=0, sticky="w")
        self.loop_int_var = tk.StringVar(value="5.0")
        self.loop_int_var.trace_add("write", lambda *args: self.update_preview())
        tk.Entry(time_frame, textvariable=self.loop_int_var, width=8).grid(row=3, column=1, padx=5, sticky="w")

        tk.Label(time_frame, text="輪詢隨機率 (±%):", fg="#f0ad4e").grid(row=4, column=0, sticky="w")
        self.loop_rand_scale = tk.Scale(time_frame, from_=0, to=10, orient=tk.HORIZONTAL, command=lambda x: self.update_preview())
        self.loop_rand_scale.set(50)
        self.loop_rand_scale.grid(row=4, column=1, sticky="we")

        # --- 預覽面板 ---
        self.preview_frame = tk.Frame(time_frame, bg="#fcfcfc", relief="groove", bd=1)
        self.preview_frame.grid(row=5, columnspan=2, sticky="we", pady=10)
        
        self.k_preview_label = tk.Label(self.preview_frame, text="", font=("Consolas", 9), bg="#fcfcfc", fg="#31708f")
        self.k_preview_label.pack(pady=2)
        self.l_preview_label = tk.Label(self.preview_frame, text="", font=("Consolas", 9), bg="#fcfcfc", fg="#8a6d3b")
        self.l_preview_label.pack(pady=2)

        # 3. 狀態與控制
        self.status_label = tk.Label(root, text="狀態: 準備就緒", fg="gray", font=("Microsoft JhengHei", 10))
        self.status_label.pack(pady=5)

        ctrl_frame = tk.Frame(root)
        ctrl_frame.pack(pady=10)
        self.start_btn = tk.Button(ctrl_frame, text="啟動循環", bg="#90EE90", width=15, height=2, command=self.start_script, font=("Microsoft JhengHei", 9, "bold"))
        self.start_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn = tk.Button(ctrl_frame, text="停止", bg="#FFB6C1", width=15, height=2, command=self.stop_script, font=("Microsoft JhengHei", 9, "bold"), state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        keyboard.on_press(self.on_key_pressed)
        self.update_preview()

    def update_preview(self):
        try:
            # 計算按鍵隨機範圍
            k_ratio = self.key_rand_scale.get() / 100.0
            k_base = float(self.key_int_var.get())
            k_min, k_max = max(0.01, k_base * (1 - k_ratio)), k_base * (1 + k_ratio)
            self.k_preview_label.config(text=f"按鍵抖動範圍: {k_min:.2f}s ~ {k_max:.2f}s")

            # 計算輪詢隨機範圍
            l_ratio = self.loop_rand_scale.get() / 100.0
            l_base = float(self.loop_int_var.get())
            l_min, l_max = max(0.01, l_base * (1 - l_ratio)), l_base * (1 + l_ratio)
            self.l_preview_label.config(text=f"輪詢休息範圍: {l_min:.2f}s ~ {l_max:.2f}s")
        except ValueError: pass

    def get_randomized_time(self, base_time, scale_val):
        ratio = scale_val / 100.0
        variation = base_time * ratio
        return max(0.01, random.uniform(base_time - variation, base_time + variation))

    def run_loop(self):
        while self.is_running:
            for key in self.key_list:
                if not self.is_running: break
                try:
                    hold = random.uniform(0.05, 0.15)
                    self.status_label.config(text=f"執行: {key}", fg="green")
                    pydirectinput.keyDown(key)
                    time.sleep(hold)
                    pydirectinput.keyUp(key)
                    # 使用按鍵專用的隨機條
                    time.sleep(self.get_randomized_time(self.k_int, self.key_rand_scale.get()))
                except: pass

            if not self.is_running: break
            
            # 使用輪詢專用的隨機條
            wait = self.get_randomized_time(self.l_int, self.loop_rand_scale.get())
            temp_wait = wait
            while temp_wait > 0 and self.is_running:
                self.status_label.config(text=f"休息中... 目標 {wait:.1f}s (剩餘 {temp_wait:.1f}s)", fg="#FFA500")
                time.sleep(0.1)
                temp_wait -= 0.1

    # --- 基礎控制 (同前版) ---
    def on_key_pressed(self, event):
        if self.is_recording:
            name = event.name.lower() if len(event.name) == 1 else event.name
            self.key_list.append(name)
            self.update_key_display()

    def toggle_record(self):
        self.is_recording = not self.is_recording
        self.record_btn.config(text="錄製中..." if self.is_recording else "開始錄製", bg="#FFD700" if self.is_recording else "#ADD8E6")

    def clear_keys(self):
        self.key_list = []; self.update_key_display()

    def update_key_display(self):
        self.key_display.config(state='normal')
        self.key_display.delete('1.0', tk.END)
        self.key_display.insert(tk.END, " → ".join(self.key_list))
        self.key_display.config(state='disabled'); self.key_display.see(tk.END)

    def start_script(self):
        if not self.key_list: return
        try:
            self.k_int = float(self.key_int_var.get())
            self.l_int = float(self.loop_int_var.get())
            self.is_running = True
            self.start_btn["state"], self.stop_btn["state"] = "disabled", "normal"
            threading.Thread(target=self.run_loop, daemon=True).start()
        except: messagebox.showerror("錯誤", "數值格式不正確")

    def stop_script(self):
        self.is_running = False
        self.status_label.config(text="狀態: 已停止", fg="red")
        self.start_btn["state"], self.stop_btn["state"] = "normal", "disabled"

if __name__ == "__main__":
    root = tk.Tk()
    app = GameAutoClicker(root)
    root.attributes('-topmost', True)
    root.mainloop()