import tkinter as tk
from tkinter import font as tkfont, simpledialog, messagebox, Menu, Toplevel, filedialog
import os
import json
import random
import re
import threading
import chardet
from PIL import ImageGrab
import mouse
import keyboard
import base64


class MoyuReader:
    def __init__(self):
        self.config_file = "config.json"
        self.load_config()

        # 初始化变量
        self.row = 0
        self.segment_index = 0
        self.text_segments = []
        self.is_monitoring_active = True
        self.chapters = []  # 存储章节 (行号, 标题)
        self.book_folder = os.path.dirname(os.path.abspath(self.file_path))  # 默认书库为当前文件目录

        # 加载文本
        self.load_file_content()

        # 初始化 UI
        self.root = tk.Tk()
        self.setup_window()
        self.setup_icon()
        self.setup_components()
        self.setup_events()

        # 启动监控
        self.start_hooks()

        # 恢复上次进度
        self.load_progress()
        self.display_text()

        # 启动背景自适应 (独立线程防止卡顿)
        self.stop_style_thread = False
        self.style_thread = threading.Thread(target=self.periodic_style_loop, daemon=True)
        self.style_thread.start()

    def load_config(self):
        default_config = {
            "file_path": "novel.txt",
            "chinese_fill_chars": "这是我的星球",
            "font_family": "微软雅黑",
            "font_size": 12,
            "window_width": 400,
            "window_height": 100,
            "window_x": 100,
            "window_y": 100,
            "scale_factor": 1,
            "code": "utf-8",
            "last_book_folder": ""  # 新增：记忆上次的书库位置
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except:
                self.config = default_config
        else:
            self.config = default_config

        # 路径处理
        self.file_path = self.config.get("file_path", "")
        # 如果配置中有保存的书库目录，就用保存的
        if self.config.get("last_book_folder"):
            self.book_folder = self.config["last_book_folder"]

        self.update_memo_path()

    def update_memo_path(self):
        """根据当前文件路径更新存档路径"""
        if self.file_path:
            self.memo_path = self.file_path[:-4] + "_memo.txt"
        else:
            self.memo_path = "reader.memo"

    def get_encoding(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                raw = f.read(20480)
            result = chardet.detect(raw)
            return result['encoding'] if result['encoding'] else 'utf-8'
        except:
            return 'utf-8'

    def load_file_content(self):
        if not os.path.exists(self.file_path):
            # 如果文件不存在，不要直接弹窗报错卡死初始化，而是显示提示
            self.lines = ["请右键打开书库选择小说文件"]
            self.total_lines = 1
            return

        encoding = self.get_encoding(self.file_path)
        try:
            with open(self.file_path, encoding=encoding, errors='ignore') as f:
                self.lines = []
                self.chapters = []  # 清空旧章节
                # 预编译正则，提高速度
                chapter_pattern = re.compile(r"^\s*(第[0-9零一二三四五六七八九十百千]+[章节回].*)")

                raw_lines = f.readlines()
                valid_line_count = 0

                for line in raw_lines:
                    s_line = line.strip()
                    if s_line:
                        self.lines.append(s_line)
                        if chapter_pattern.match(s_line):
                            self.chapters.append((valid_line_count, s_line))
                        valid_line_count += 1

            # 记录当前书库目录，以便下次使用
            self.book_folder = os.path.dirname(os.path.abspath(self.file_path))

        except Exception as e:
            self.lines = [f"读取错误: {e}"]

        self.total_lines = len(self.lines)
        print(f"已加载: {os.path.basename(self.file_path)}，{self.total_lines}行")

    def setup_window(self):
        w = self.config.get("window_width", 400)
        h = self.config.get("window_height", 100)
        x = self.config.get("window_x", 100)
        y = self.config.get("window_y", 100)

        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.wm_attributes("-transparentcolor", "#F1F1F1")

    def setup_icon(self):
        # 这是一个简单的“书本”图标的 Base64 编码
        # 如果你想换图标，可以在网上找 "Image to Base64" 工具，把生成的字符串替换下面引号里的内容
        icon_base64 = """
        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
        """
        try:
            # 移除空白字符
            img_data = base64.b64decode(icon_base64.strip())
            # 创建 PhotoImage 对象
            self.icon_image = tk.PhotoImage(data=img_data)
            # 设置窗口图标 (True 表示应用到所有子窗口)
            self.root.iconphoto(True, self.icon_image)
        except Exception as e:
            print(f"图标加载失败: {e}")

    def setup_components(self):
        self.font = tkfont.Font(family=self.config.get("font_family", "微软雅黑"),
                                size=self.config.get("font_size", 10))

        self.text_box = tk.Text(self.root, wrap=tk.WORD, font=self.font,
                                bg="#F1F1F1", fg="black", bd=0, highlightthickness=0)
        self.text_box.pack(expand=True, fill="both")

        # 右键菜单
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="📖 打开书库", command=self.open_library_window)  # 新增
        self.context_menu.add_command(label="🔍 搜索内容", command=self.search_text)
        self.context_menu.add_command(label="📚 章节目录", command=self.show_chapter_list)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ 退出程序", command=self.on_close)

    def setup_events(self):
        self.text_box.bind("<Button-3>", self.on_right_click)
        self.text_box.bind("<B3-Motion>", self.on_window_drag)
        self.text_box.bind("<ButtonRelease-3>", self.on_right_release)
        self.text_box.bind("<Button-2>", self.start_resize)
        self.text_box.bind("<B2-Motion>", self.perform_resize)
        self.text_box.bind("<Configure>", lambda e: self.display_text())

        self._drag_data = {"x": 0, "y": 0, "moved": False}

    def start_hooks(self):
        self.mouse_hook = mouse.on_click(self.next_page)
        keyboard.add_hotkey('down', self.next_page)
        keyboard.add_hotkey('up', self.prev_page)
        keyboard.add_hotkey('alt+up', lambda: self.adjust_font(1))
        keyboard.add_hotkey('alt+down', lambda: self.adjust_font(-1))
        keyboard.add_hotkey('ctrl+alt', self.toggle_monitoring)

    # ================= 核心逻辑 =================

    def calculate_stepl(self):
        char_width = self.font.measure("字")
        return max(1, self.root.winfo_width() // char_width)

    def display_text(self):
        if not self.lines: return

        if self.row >= self.total_lines: self.row = self.total_lines - 1
        if self.row < 0: self.row = 0

        line = self.lines[self.row]
        stepl = self.calculate_stepl()

        self.text_segments = [line[i:i + stepl] for i in range(0, len(line), stepl)]

        if self.segment_index >= len(self.text_segments):
            self.segment_index = 0

        self.show_segment()

    def show_segment(self):
        if not self.text_segments: return

        self.text_box.delete(1.0, tk.END)
        if self.segment_index < len(self.text_segments):
            text = self.text_segments[self.segment_index]
            padding = self.config.get("chinese_fill_chars", " ")
            if len(padding) > 0:
                text = text.ljust(self.calculate_stepl(), random.choice(padding))
            self.text_box.insert(tk.END, text)

    def next_page(self):
        if not self.is_monitoring_active: return
        if not self.lines: return  # 防止空内容报错

        if self.segment_index < len(self.text_segments) - 1:
            self.segment_index += 1
            self.show_segment()
        elif self.row < self.total_lines - 1:
            self.row += 1
            self.segment_index = 0
            self.display_text()
            self.save_progress()

    def prev_page(self):
        if not self.is_monitoring_active: return
        if not self.lines: return

        if self.segment_index > 0:
            self.segment_index -= 1
            self.show_segment()
        elif self.row > 0:
            self.row -= 1
            self.display_text()
            self.segment_index = max(0, len(self.text_segments) - 1)
            self.show_segment()
            self.save_progress()

    # ================= 新增功能：书库 =================

    def open_library_window(self):
        self.is_monitoring_active = False  # 暂停翻页

        lib_win = Toplevel(self.root)
        lib_win.title("我的书库")
        lib_win.geometry("400x300")
        lib_win.attributes('-topmost', True)

        # 顶部工具栏
        frame_top = tk.Frame(lib_win)
        frame_top.pack(fill=tk.X, padx=5, pady=5)

        lbl_path = tk.Label(frame_top, text=f"当前目录: ...{self.book_folder[-20:]}", fg="gray")
        lbl_path.pack(side=tk.LEFT)

        btn_change = tk.Button(frame_top, text="📂 切换目录",
                               command=lambda: self.change_lib_folder(lib_win, listbox, lbl_path))
        btn_change.pack(side=tk.RIGHT)

        # 文件列表
        listbox = tk.Listbox(lib_win, font=("微软雅黑", 10), selectmode=tk.SINGLE)
        scrollbar = tk.Scrollbar(lib_win, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.refresh_file_list(listbox)

        # 双击打开
        def open_selected(event):
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                # === 修改点：通过索引从 library_paths 获取绝对路径 ===
                # 防止点击到"没有找到txt小说"等提示文字报错
                if index < len(self.library_paths):
                    full_path = self.library_paths[index]
                    self.switch_book(full_path)
                    lib_win.destroy()

        listbox.bind("<Double-Button-1>", open_selected)

        def on_lib_close():
            self.is_monitoring_active = True
            lib_win.destroy()

        lib_win.protocol("WM_DELETE_WINDOW", on_lib_close)

    def change_lib_folder(self, win, listbox, lbl_path):
        folder = filedialog.askdirectory(parent=win, initialdir=self.book_folder)
        if folder:
            self.book_folder = folder
            lbl_path.config(text=f"当前目录: ...{self.book_folder[-20:]}")
            self.refresh_file_list(listbox)
            # 保存书库位置
            self.config["last_book_folder"] = folder

    def refresh_file_list(self, listbox):
        listbox.delete(0, tk.END)
        self.library_paths = []
        if not os.path.isdir(self.book_folder):
            listbox.insert(tk.END, "目录无效")
            return

        try:
            for root, dirs, files in os.walk(self.book_folder):
                for f in files:
                    # 过滤逻辑：必须是txt，且不是memo文件，不是config文件
                    if f.lower().endswith('.txt') and 'memo' not in f and 'config' not in f:
                        full_path = os.path.join(root, f)
                        # 计算相对路径（例如：子文件夹/小说.txt），用于在界面显示
                        rel_path = os.path.relpath(full_path, self.book_folder)

                        self.library_paths.append(full_path)
                        listbox.insert(tk.END, rel_path)

            if not self.library_paths:
                listbox.insert(tk.END, "没有找到txt小说")
        except Exception as e:
            listbox.insert(tk.END, f"读取错误: {str(e)}")

    def switch_book(self, new_path):
        # 保存当前书籍的进度
        self.save_progress()

        # 切换路径
        self.file_path = new_path
        self.config["file_path"] = new_path
        self.update_memo_path()

        # 重置状态
        self.row = 0
        self.segment_index = 0

        # 加载新书
        self.load_file_content()
        self.load_progress()  # 如果这本新书有存档，则读取
        self.display_text()

        self.is_monitoring_active = True
        print(f"已切换至: {new_path}")

    # ================= 章节与搜索 (原有逻辑微调) =================

    def show_chapter_list(self):
        self.is_monitoring_active = False
        top = Toplevel(self.root)
        top.title("章节目录")
        top.geometry("300x400")
        top.attributes('-topmost', True)

        listbox = tk.Listbox(top, font=("微软雅黑", 10))
        scrollbar = tk.Scrollbar(top, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if not self.chapters:
            listbox.insert(tk.END, "未检测到章节")
        else:
            for idx, (line_num, title) in enumerate(self.chapters):
                listbox.insert(tk.END, title)
                if self.row >= line_num:
                    listbox.see(idx)
                    listbox.activate(idx)

        def jump_to_chapter(event):
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                target_row = self.chapters[idx][0]
                self.row = target_row
                self.segment_index = 0
                self.display_text()
                self.save_progress()
                self.is_monitoring_active = True
                top.destroy()

        listbox.bind("<Double-Button-1>", jump_to_chapter)
        top.protocol("WM_DELETE_WINDOW", lambda: (setattr(self, 'is_monitoring_active', True), top.destroy()))

    def search_text(self):
        self.is_monitoring_active = False
        query = simpledialog.askstring("搜索", "输入关键字:", parent=self.root)
        self.is_monitoring_active = True

        if not query: return

        found = False
        for i in range(self.row, self.total_lines):
            if query in self.lines[i]:
                self.row = i
                self.segment_index = 0
                self.display_text()
                found = True
                break

        if not found:
            for i in range(0, self.row):
                if query in self.lines[i]:
                    self.row = i
                    self.segment_index = 0
                    self.display_text()
                    found = True
                    break

        if found:
            self.save_progress()
        else:
            messagebox.showinfo("提示", "未找到该内容")

    # ================= 辅助功能 =================

    def adjust_font(self, delta):
        size = self.font.cget("size")
        new_size = max(6, size + delta)
        self.font.config(size=new_size)
        self.config["font_size"] = new_size
        self.display_text()

    def toggle_monitoring(self):
        self.is_monitoring_active = not self.is_monitoring_active
        print(f"监控状态: {'开启' if self.is_monitoring_active else '暂停'}")

    def save_progress(self):
        if not self.lines: return
        try:
            with open(self.memo_path, "w", encoding='utf-8') as f:
                f.write(str(self.row))
        except:
            pass

    def load_progress(self):
        self.row = 0
        if os.path.exists(self.memo_path):
            try:
                with open(self.memo_path, "r", encoding='utf-8') as f:
                    val = f.read().strip()
                    if val.isdigit():
                        self.row = int(val)
            except:
                pass

    # ================= 样式与事件 =================

    def periodic_style_loop(self):
        import time
        while not self.stop_style_thread:
            self.root.after(0, self.calculate_coords_safely)
            try:
                self.screenshot_and_update()
            except:
                pass
            time.sleep(0.5)

    def calculate_coords_safely(self):
        """【主线程执行】安全的计算坐标"""
        try:
            # === 这里完全使用你之前的逻辑 ===
            bbox = self.text_box.bbox("1.0")
            if not bbox:
                return

            char_x, char_y, char_w, char_h = bbox

            # 加上 rootx/y 转换为屏幕绝对坐标
            win_x = self.root.winfo_rootx()
            win_y = self.root.winfo_rooty()
            tb_x = self.text_box.winfo_x()
            tb_y = self.text_box.winfo_y()

            logical_x = win_x + tb_x + char_x - 2
            logical_y = win_y + tb_y + char_y + char_h // 2

            # 考虑缩放
            scale = self.config.get("scale_factor", 1)

            # 将算好的坐标存入 self 变量，供后台线程取用
            self.current_sample_x = int(logical_x * scale)
            self.current_sample_y = int(logical_y * scale)

        except Exception as e:
            # 窗口最小化或关闭时可能会报错，忽略即可
            pass

    def screenshot_and_update(self):
        """【子线程执行】耗时的截屏和分析"""
        # 如果坐标还没算出来（程序刚启动），就先不动
        if not hasattr(self, 'current_sample_x'):
            return

        px = self.current_sample_x
        py = self.current_sample_y

        # 截取 1x1 像素
        image = ImageGrab.grab(bbox=(px, py, px + 1, py + 1))
        color = image.getpixel((0, 0))

        # 计算亮度
        luminance = (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]) / 255
        bg_hex = '#%02x%02x%02x' % color
        fg_color = "black" if luminance > 0.5 else "white"

        # 【再回到主线程】应用颜色
        def _apply_style():
            try:
                self.text_box.config(bg=bg_hex, fg=fg_color)
                self.root.wm_attributes("-transparentcolor", bg_hex)
            except:
                pass

        self.root.after(0, _apply_style)

    def on_right_click(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._drag_data["moved"] = False

    def on_window_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.root.geometry(f"+{self.root.winfo_x() + dx}+{self.root.winfo_y() + dy}")
        self._drag_data["moved"] = True

    def on_right_release(self, event):
        if not self._drag_data["moved"]:
            self.context_menu.post(event.x_root, event.y_root)

    def start_resize(self, event):
        self._resize_data = {'x': event.x, 'y': event.y, 'w': self.root.winfo_width(), 'h': self.root.winfo_height()}

    def perform_resize(self, event):
        dx = event.x - self._resize_data['x']
        dy = event.y - self._resize_data['y']
        self.root.geometry(f"{max(100, self._resize_data['w'] + dx)}x{max(50, self._resize_data['h'] + dy)}")

    def on_close(self):
        self.stop_style_thread = True
        self.save_progress()
        self.config.update({
            'window_width': self.root.winfo_width(),
            'window_height': self.root.winfo_height(),
            'window_x': self.root.winfo_x(),
            'window_y': self.root.winfo_y(),
            'last_book_folder': self.book_folder
        })
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        mouse.unhook_all()
        keyboard.unhook_all_hotkeys()
        self.root.destroy()
        os._exit(0)


if __name__ == "__main__":
    app = MoyuReader()
    app.root.mainloop()
