import tkinter as tk
from tkinter import messagebox, font
import threading
import time
import random
import keyboard
import pydirectinput
import ctypes

pydirectinput.FAILSAFE = True

# ---------- 現代化配色方案 ----------
COLORS = {
    "bg": "#F8F9FA",
    "card": "#FFFFFF",
    "primary": "#5E35B1",
    "primary_hover": "#7E57C2",
    "secondary": "#00BFA5",
    "secondary_hover": "#1DE9B6",
    "danger": "#E53935",
    "danger_hover": "#F44336",
    "success": "#43A047",
    "warning": "#FFA726",
    "text": "#212121",
    "sub": "#616161",
    "divider": "#E0E0E0",
    "input": "#FAFAFA",
    "record": "#FF6F00",
    "record_active": "#FFD54F"
}

class ModernButton(tk.Button):
    """現代化按鈕組件"""
    def __init__(self, master, style="primary", **kwargs):
        defaults = {
            "font": ("Segoe UI", 10),
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2",
            "padx": 20,
            "pady": 10,
            "fg": "white"
        }
        
        if style == "primary":
            defaults["bg"] = COLORS["primary"]
            defaults["activebackground"] = COLORS["primary_hover"]
        elif style == "secondary":
            defaults["bg"] = COLORS["secondary"]
            defaults["activebackground"] = COLORS["secondary_hover"]
        elif style == "danger":
            defaults["bg"] = COLORS["danger"]
            defaults["activebackground"] = COLORS["danger_hover"]
        elif style == "record":
            defaults["bg"] = COLORS["record"]
            defaults["activebackground"] = COLORS["record_active"]
        
        defaults.update(kwargs)
        super().__init__(master, **defaults)
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.default_bg = defaults["bg"]
        self.hover_bg = defaults["activebackground"]
    
    def _on_enter(self, e):
        if self["state"] != "disabled":
            self["bg"] = self.hover_bg
    
    def _on_leave(self, e):
        if self["state"] != "disabled":
            self["bg"] = self.default_bg

class MaterialCard(tk.Frame):
    """Material Design 卡片組件"""
    def __init__(self, master, title=None):
        super().__init__(
            master, 
            bg=COLORS["card"],
            padx=20, 
            pady=15
        )
        
        self.configure(
            highlightbackground="#D0D0D0",
            highlightthickness=1,
            relief="flat"
        )
        
        if title:
            tk.Label(
                self, 
                text=title,
                font=("Segoe UI", 11, "bold"), 
                fg=COLORS["primary"],
                bg=COLORS["card"]
            ).pack(anchor="w", pady=(0, 10))

class GameAutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClick")
        self.root.geometry("500x900")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg"])

        # 啟動時切換到英文輸入法
        self.set_english_input()

        # 狀態變數 - 全部用 lock 保護
        self.is_running = False
        self.is_recording = False
        self.key_list = []
        self.total_cycles = 0
        self.start_time = None
        self.current_loop = 0
        
        # 執行緒安全鎖
        self.lock = threading.Lock()
        
        # 用於安全關閉的標記
        self.is_closing = False
        self.stats_timer_id = None

        # 字體設定
        self.font_h1 = font.Font(family="Segoe UI", size=16, weight="bold")
        self.font_h2 = font.Font(family="Segoe UI", size=11, weight="bold")
        self.font_code = font.Font(family="Consolas", size=10)
        self.font_small = font.Font(family="Segoe UI", size=9)

        self.build_ui()
        
        # 註冊鍵盤監聽
        try:
            keyboard.on_press(self.on_key_pressed)
            # 註冊熱鍵停止功能 (Ctrl+Shift+Q)
            keyboard.add_hotkey('ctrl+shift+q', self.emergency_stop)
        except Exception as e:
            messagebox.showerror("錯誤", "鍵盤監聽初始化失敗，請以管理員身份運行")
        
        self.update_preview()
        
        # 定期更新統計資訊
        self.update_stats()

    def set_english_input(self):
        """切換到英文輸入法 (Windows)"""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            ctypes.windll.user32.PostMessageW(hwnd, 0x50, 0, 0x4090409)
        except:
            pass

    def emergency_stop(self):
        """緊急停止熱鍵處理"""
        with self.lock:
            if self.is_running:
                self.ui(self.stop)

    # ---------- UI 建構 ----------
    def build_ui(self):
        # 頂部標題欄
        header = tk.Frame(self.root, bg=COLORS["primary"], height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header, 
            text="🎮 自動按鍵序列工具",
            bg=COLORS["primary"], 
            fg="white",
            font=self.font_h1
        ).pack(pady=(12, 5))
        
        tk.Label(
            header, 
            text="Made by Hank | Pray For Trump阿杰 | 緊急停止：Ctrl+Shift+Q",
            bg=COLORS["primary"], 
            fg="#E1BEE7",
            font=self.font_small
        ).pack(pady=(0, 10))

        # 主容器
        main_container = tk.Frame(self.root, bg=COLORS["bg"])
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # --- Card 1: 按鍵錄製 ---
        card1 = MaterialCard(main_container, title="📝 1. 按鍵序列錄製")
        card1.pack(fill="x", pady=(0, 15))

        # 按鍵顯示區域
        display_frame = tk.Frame(card1, bg=COLORS["input"], bd=1, relief="solid")
        display_frame.pack(fill="x", pady=10)
        
        self.key_display = tk.Text(
            display_frame, 
            height=4, 
            state="disabled",
            bg=COLORS["input"], 
            bd=0,
            font=self.font_code,
            wrap="word",
            padx=10,
            pady=8
        )
        self.key_display.pack(fill="x")

        # 按鍵計數
        self.key_count_label = tk.Label(
            card1,
            text="已錄製: 0 個按鍵",
            bg=COLORS["card"],
            fg=COLORS["sub"],
            font=self.font_small
        )
        self.key_count_label.pack(anchor="w", pady=(5, 10))

        # 按鈕列
        btn_row = tk.Frame(card1, bg=COLORS["card"])
        btn_row.pack(fill="x")

        self.record_btn = ModernButton(
            btn_row, 
            text="🔴 開始錄製",
            style="record",
            command=self.toggle_record
        )
        self.record_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.clear_btn = ModernButton(
            btn_row, 
            text="🗑️ 清空",
            style="danger",
            command=self.clear_keys
        )
        self.clear_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))

        # --- Card 2: 時間設定 ---
        card2 = MaterialCard(main_container, title="⏱️ 2. 時間間隔設定")
        card2.pack(fill="x", pady=(0, 15))

        self.key_base = tk.StringVar(value="0.2")
        self.key_scale = tk.StringVar(value="100")
        self.key_scale_max = tk.StringVar(value="200")
        
        self.loop_base = tk.StringVar(value="5.0")
        self.loop_scale = tk.StringVar(value="10")
        self.loop_scale_max = tk.StringVar(value="100")

        # 為變數添加追蹤
        for v in [self.key_base, self.key_scale, self.loop_base, self.loop_scale]:
            v.trace_add("write", lambda *_: self.update_preview())

        # 按鍵間隔設定
        self.create_timing_setting(
            card2, 
            "⌨️ 按鍵間隔 (秒)", 
            self.key_base, 
            self.key_scale,
            self.key_scale_max,
            is_key=True
        )
        
        tk.Frame(card2, height=2, bg=COLORS["divider"]).pack(fill="x", pady=15)
        
        # 循環休息設定
        self.create_timing_setting(
            card2, 
            "🔄 整輪休息 (秒)", 
            self.loop_base, 
            self.loop_scale,
            self.loop_scale_max,
            is_key=False
        )

        # 預覽標籤
        preview_frame = tk.Frame(card2, bg=COLORS["input"], bd=1, relief="solid")
        preview_frame.pack(fill="x", pady=10)
        
        self.preview = tk.Label(
            preview_frame,
            bg=COLORS["input"],
            fg=COLORS["text"], 
            font=("Consolas", 9),
            padx=10,
            pady=8
        )
        self.preview.pack(fill="x")

        # --- Card 3: 執行控制 ---
        card3 = MaterialCard(main_container, title="🎯 3. 執行控制")
        card3.pack(fill="x", pady=(0, 15))

        ctrl = tk.Frame(card3, bg=COLORS["card"])
        ctrl.pack(fill="x", pady=5)

        self.start_btn = ModernButton(
            ctrl, 
            text="▶️ 開始執行", 
            style="primary",
            command=self.start
        )
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.stop_btn = ModernButton(
            ctrl, 
            text="⏹️ 停止", 
            style="danger",
            state="disabled", 
            command=self.stop
        )
        self.stop_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))

        # 狀態顯示
        status_frame = tk.Frame(card3, bg=COLORS["input"], bd=1, relief="solid")
        status_frame.pack(fill="x", pady=10)
        
        self.status = tk.Label(
            status_frame,
            text="✅ 準備就緒",
            fg=COLORS["text"], 
            bg=COLORS["input"],
            font=("Segoe UI", 10),
            padx=10,
            pady=8
        )
        self.status.pack(fill="x")

        # 當前按鍵顯示
        current_key_frame = tk.Frame(card3, bg=COLORS["card"])
        current_key_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(
            current_key_frame,
            text="當前按鍵:",
            bg=COLORS["card"],
            fg=COLORS["sub"],
            font=self.font_small
        ).pack(side="left")
        
        self.current_key_label = tk.Label(
            current_key_frame,
            text="-",
            bg=COLORS["card"],
            fg=COLORS["primary"],
            font=("Segoe UI", 14, "bold")
        )
        self.current_key_label.pack(side="left", padx=10)

        # --- Card 4: 統計資訊 ---
        card4 = MaterialCard(main_container, title="📊 執行統計")
        card4.pack(fill="x")

        stats_grid = tk.Frame(card4, bg=COLORS["card"])
        stats_grid.pack(fill="x")

        # 統計標籤
        self.stats_cycles = self.create_stat_label(stats_grid, "執行循環", "0", 0, 0)
        self.stats_time = self.create_stat_label(stats_grid, "運行時間", "00:00:00", 0, 1)
        self.stats_loop = self.create_stat_label(stats_grid, "整輪倒數", "-", 1, 0)
        self.stats_keys = self.create_stat_label(stats_grid, "總按鍵數", "0", 1, 1)

        # 底部提示
        tip_frame = tk.Frame(self.root, bg=COLORS["bg"])
        tip_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        tk.Label(
            tip_frame,
            text="💡 提示: 按 Ctrl+Shift+Q 可緊急停止 | 移動滑鼠到螢幕角落也可觸發安全停止",
            bg=COLORS["bg"],
            fg=COLORS["sub"],
            font=self.font_small
        ).pack()

    def create_stat_label(self, parent, title, value, row, col):
        """創建統計標籤"""
        frame = tk.Frame(parent, bg=COLORS["input"], bd=1, relief="solid")
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        parent.columnconfigure(col, weight=1)
        
        tk.Label(
            frame,
            text=title,
            bg=COLORS["input"],
            fg=COLORS["sub"],
            font=self.font_small
        ).pack(pady=(8, 0))
        
        label = tk.Label(
            frame,
            text=value,
            bg=COLORS["input"],
            fg=COLORS["primary"],
            font=("Segoe UI", 12, "bold")
        )
        label.pack(pady=(0, 8))
        
        return label

    def create_timing_setting(self, parent, label_text, base_var, scale_var, scale_max_var, is_key):
        """創建時間設定區塊"""
        frame = tk.Frame(parent, bg=COLORS["card"])
        frame.pack(fill="x", pady=5)

        # 標籤
        tk.Label(
            frame, 
            text=label_text, 
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 5))

        # 輸入框容器
        input_frame = tk.Frame(frame, bg=COLORS["card"])
        input_frame.pack(fill="x")

        # 基準時間輸入
        entry_frame = tk.Frame(input_frame, bg=COLORS["card"])
        entry_frame.pack(side="left")
        
        tk.Label(
            entry_frame,
            text="基準:",
            bg=COLORS["card"],
            fg=COLORS["sub"],
            font=self.font_small
        ).pack(side="left", padx=(0, 5))
        
        entry = tk.Entry(
            entry_frame, 
            textvariable=base_var, 
            width=8,
            font=("Consolas", 10),
            bd=1,
            relief="solid"
        )
        entry.pack(side="left")
        
        tk.Label(
            entry_frame,
            text="秒",
            bg=COLORS["card"],
            fg=COLORS["sub"],
            font=self.font_small
        ).pack(side="left", padx=(5, 0))

        # 隨機範圍設定
        scale_input_frame = tk.Frame(frame, bg=COLORS["card"])
        scale_input_frame.pack(fill="x", pady=(5, 0))
        
        tk.Label(
            scale_input_frame,
            text="隨機範圍: ±",
            bg=COLORS["card"],
            fg=COLORS["sub"],
            font=self.font_small
        ).pack(side="left")
        
        scale_entry = tk.Entry(
            scale_input_frame, 
            textvariable=scale_var, 
            width=8,
            font=("Consolas", 10),
            bd=1,
            relief="solid"
        )
        scale_entry.pack(side="left", padx=5)
        
        tk.Label(
            scale_input_frame,
            text="%   (最大值:",
            bg=COLORS["card"],
            fg=COLORS["sub"],
            font=self.font_small
        ).pack(side="left")
        
        max_entry = tk.Entry(
            scale_input_frame, 
            textvariable=scale_max_var, 
            width=6,
            font=("Consolas", 10),
            bd=1,
            relief="solid"
        )
        max_entry.pack(side="left", padx=5)
        
        tk.Label(
            scale_input_frame,
            text="%)",
            bg=COLORS["card"],
            fg=COLORS["sub"],
            font=self.font_small
        ).pack(side="left")

        # 儲存引用
        if is_key:
            self.key_entry = entry
            self.key_scale_entry = scale_entry
            self.key_scale_max_entry = max_entry
        else:
            self.loop_entry = entry
            self.loop_scale_entry = scale_entry
            self.loop_scale_max_entry = max_entry

    # ---------- 工具函數 ----------
    def ui(self, func):
        """在主線程中執行 UI 更新"""
        try:
            if not self.is_closing and self.root.winfo_exists():
                self.root.after(0, func)
        except:
            pass

    def lock_settings(self, locked: bool):
        """鎖定/解鎖設定控件"""
        state = "disabled" if locked else "normal"
        for w in [
            self.key_entry, self.loop_entry,
            self.key_scale_entry, self.loop_scale_entry,
            self.key_scale_max_entry, self.loop_scale_max_entry,
            self.record_btn, self.clear_btn
        ]:
            if w:
                try:
                    w.config(state=state)
                except:
                    pass

    def safe_float(self, var, default=1.0):
        """安全地轉換為浮點數"""
        try:
            value = float(var.get())
            return max(0.01, value)
        except:
            return default

    def safe_percent(self, var, default=10.0):
        """安全地轉換百分比"""
        try:
            value = float(var.get())
            return max(0, value)
        except:
            return default

    # ---------- 邏輯功能 ----------
    def update_preview(self):
        """更新時間預覽"""
        try:
            kb = self.safe_float(self.key_base, 0.2)
            ks = self.safe_percent(self.key_scale, 100) / 100
            lb = self.safe_float(self.loop_base, 5.0)
            ls = self.safe_percent(self.loop_scale, 10) / 100
            
            self.preview.config(
                text=f"📋 按鍵間隔: {kb*(1-ks):.3f} ~ {kb*(1+ks):.3f} 秒  |  "
                     f"循環休息: {lb*(1-ls):.2f} ~ {lb*(1+ls):.2f} 秒"
            )
        except:
            self.preview.config(text="⚠️ 請輸入正確的數值")

    def update_stats(self):
        """更新統計資訊（使用安全的 after 機制）"""
        if self.is_closing:
            return
            
        try:
            with self.lock:
                is_running = self.is_running
                start_time = self.start_time
                total_cycles = self.total_cycles
                key_list_len = len(self.key_list)
            
            if is_running and start_time:
                # 計算運行時間
                elapsed = time.time() - start_time
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = int(elapsed % 60)
                
                def update_time():
                    try:
                        self.stats_time.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
                    except:
                        pass
                
                self.ui(update_time)
                
                # 更新總按鍵數
                total_keys = total_cycles * key_list_len
                
                def update_keys():
                    try:
                        self.stats_keys.config(text=str(total_keys))
                    except:
                        pass
                
                self.ui(update_keys)
        except:
            pass
        
        # 安全的定時器重新排程
        if not self.is_closing:
            try:
                self.stats_timer_id = self.root.after(1000, self.update_stats)
            except:
                pass

    def start(self):
        """開始執行"""
        if not self.key_list:
            messagebox.showwarning("⚠️ 提示", "尚未錄製任何按鍵序列！")
            return

        try:
            # 驗證時間設定
            if self.safe_float(self.key_base) <= 0 or self.safe_float(self.loop_base) <= 0:
                messagebox.showwarning("⚠️ 提示", "時間設定必須大於 0！")
                return

            with self.lock:
                self.is_running = True
                self.start_time = time.time()
                self.total_cycles = 0
                self.current_loop = 0
            
            self.root.attributes("-topmost", True)
            self.lock_settings(True)
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            
            # 更新統計
            def reset_stats():
                try:
                    self.stats_cycles.config(text="0")
                    self.stats_loop.config(text="-")
                    self.current_key_label.config(text="-")
                except:
                    pass
            
            self.ui(reset_stats)
            
            threading.Thread(target=self.run_with_delay, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("❌ 錯誤", f"啟動失敗: {str(e)}")
            self.stop()

    def run_with_delay(self):
        """延遲啟動"""
        try:
            for i in range(3, 0, -1):
                with self.lock:
                    if not self.is_running:
                        return
                
                def update_countdown(count=i):
                    try:
                        self.status.config(text=f"⏳ {count} 秒後開始執行...")
                    except:
                        pass
                
                self.ui(update_countdown)
                time.sleep(1)

            self.run()
        except:
            self.stop()

    def stop(self):
        """停止執行"""
        with self.lock:
            self.is_running = False
        
        self.root.attributes("-topmost", False)
        self.lock_settings(False)
        
        def update_ui():
            try:
                self.status.config(text="⏹️ 已停止")
                self.stats_loop.config(text="-")
                self.current_key_label.config(text="-")
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
            except:
                pass
        
        self.ui(update_ui)

    def run(self):
        """主執行循環（修復線程安全和時間精度問題）"""
        while True:
            # 檢查是否應該停止（線程安全）
            with self.lock:
                if not self.is_running:
                    break
            
            try:
                # 執行按鍵序列
                for i, key in enumerate(self.key_list):
                    # 每次循環檢查停止標記
                    with self.lock:
                        if not self.is_running:
                            break
                    
                    # 更新當前按鍵顯示
                    def update_current_key(k=key, idx=i):
                        try:
                            self.current_key_label.config(text=k)
                            self.status.config(text=f"▶️ 執行按鍵: {k} ({idx+1}/{len(self.key_list)})")
                        except:
                            pass
                    
                    self.ui(update_current_key)
                    
                    try:
                        pydirectinput.press(key)
                    except:
                        pass
                    
                    # 使用高精度睡眠
                    self.precise_sleep(self.random_time(self.key_base, self.key_scale))

                # 完成一輪
                with self.lock:
                    self.total_cycles += 1
                    cycles = self.total_cycles
                
                def update_cycles(c=cycles):
                    try:
                        self.stats_cycles.config(text=str(c))
                    except:
                        pass
                
                self.ui(update_cycles)

                # 循環休息 - 使用高精度倒數
                wait = self.random_time(self.loop_base, self.loop_scale)
                
                # 清空當前按鍵
                def clear_current():
                    try:
                        self.current_key_label.config(text="-")
                    except:
                        pass
                
                self.ui(clear_current)
                
                # 高精度倒數（使用實際時間而非累加）
                end_time = time.perf_counter() + wait
                
                while True:
                    with self.lock:
                        if not self.is_running:
                            break
                    
                    remain = end_time - time.perf_counter()
                    
                    if remain <= 0:
                        break
                    
                    # 更新整輪倒數
                    def update_countdown(r=remain):
                        try:
                            self.stats_loop.config(text=f"{r:.1f}s")
                            self.status.config(text=f"💤 整輪休息倒數: {r:.1f} 秒")
                        except:
                            pass
                    
                    self.ui(update_countdown)
                    time.sleep(0.05)  # 更短的睡眠時間以提高響應性

            except Exception as e:
                print(f"執行錯誤: {e}")
                time.sleep(1)

    def precise_sleep(self, duration):
        """高精度睡眠（處理可中斷的情況）"""
        end_time = time.perf_counter() + duration
        while time.perf_counter() < end_time:
            with self.lock:
                if not self.is_running:
                    break
            # 使用短睡眠以保持響應性
            remaining = end_time - time.perf_counter()
            if remaining > 0:
                time.sleep(min(0.001, remaining))

    def random_time(self, base_var, scale_var):
        """計算隨機時間"""
        try:
            base = self.safe_float(base_var)
            ratio = self.safe_percent(scale_var) / 100
            min_time = base * (1 - ratio)
            max_time = base * (1 + ratio)
            return max(0.01, random.uniform(min_time, max_time))
        except:
            return 1.0

    # ---------- 按鍵錄製 ----------
    def on_key_pressed(self, e):
        """按鍵按下事件"""
        with self.lock:
            is_recording = self.is_recording
        
        if is_recording and e.name and e.name != "unknown":
            try:
                self.key_list.append(e.name)
                self.update_keys()
            except:
                pass

    def toggle_record(self):
        """切換錄製狀態"""
        with self.lock:
            self.is_recording = not self.is_recording
            is_recording = self.is_recording
        
        if is_recording:
            self.record_btn.config(
                text="⏺️ 錄製中（點此停止）"
            )
            self.record_btn.default_bg = COLORS["record_active"]
            self.record_btn.hover_bg = COLORS["warning"]
            self.record_btn["bg"] = COLORS["record_active"]
            
            def update_status():
                try:
                    self.status.config(text="🔴 錄製中... 請按下需要的按鍵")
                except:
                    pass
            
            self.ui(update_status)
        else:
            self.record_btn.config(
                text="🔴 開始錄製"
            )
            self.record_btn.default_bg = COLORS["record"]
            self.record_btn.hover_bg = COLORS["record_active"]
            self.record_btn["bg"] = COLORS["record"]
            
            def update_status():
                try:
                    self.status.config(text="✅ 準備就緒")
                except:
                    pass
            
            self.ui(update_status)

    def clear_keys(self):
        """清空按鍵"""
        if self.key_list and not messagebox.askyesno(
            "⚠️ 確認", 
            f"確定要清空已錄製的 {len(self.key_list)} 個按鍵嗎？"
        ):
            return
        
        self.key_list.clear()
        self.update_keys()

    def update_keys(self):
        """更新按鍵顯示"""
        self.key_display.config(state="normal")
        self.key_display.delete("1.0", tk.END)
        
        if self.key_list:
            display_text = " → ".join(self.key_list)
            self.key_display.insert(tk.END, display_text)
        else:
            self.key_display.insert(tk.END, "尚未錄製任何按鍵...")
        
        self.key_display.config(state="disabled")
        
        self.key_count_label.config(
            text=f"已錄製: {len(self.key_list)} 個按鍵"
        )

    def cleanup(self):
        """清理資源"""
        self.is_closing = True
        
        # 停止執行
        with self.lock:
            self.is_running = False
        
        # 取消定時器
        if self.stats_timer_id:
            try:
                self.root.after_cancel(self.stats_timer_id)
            except:
                pass
        
        # 移除鍵盤監聽
        try:
            keyboard.unhook_all()
        except:
            pass


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = GameAutoClicker(root)
        
        # 設定關閉事件
        def on_closing():
            with app.lock:
                is_running = app.is_running
            
            if is_running:
                if messagebox.askyesno("確認", "程式正在執行中，確定要關閉嗎？"):
                    app.cleanup()
                    root.destroy()
            else:
                app.cleanup()
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("❌ 嚴重錯誤", f"應用程式無法啟動:\n{str(e)}")
