import tkinter as tk
import os
import random
import mouse
import keyboard
from tkinter import font as tkfont
from PIL import ImageGrab
import json
import chardet



# 读取 JSON 配置
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# 从配置中加载变量
file = config["file_path"]
file_memo = file[:-4] + "_memo.txt"
chinese_fill_chars = config["chinese_fill_chars"]
font_family = config["font_family"]
font_size = config["font_size"]
code = config["code"]
window_width = config["window_width"]
window_height = config["window_height"]
window_x = config["window_x"]
window_y = config["window_y"]



# 设置您的变量和文件路径
chinese_fill_chars = chinese_fill_chars
# chinese_fill_chars = "星"
row = 0

CACHE_FILE = "config.json"

def get_file_encoding(file_path):
    # 检查缓存文件是否存在
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as cache_file:
            cache = json.load(cache_file)
    else:
        cache = {}

    # 获取文件的修改时间
    file_mtime = os.path.getmtime(file_path)

    # 如果文件的编码已缓存且未更新，直接返回缓存结果
    if file_path in cache and cache[file_path]['mtime'] == file_mtime:
        print(f"使用缓存的编码结果: {cache[file_path]['encoding']}")
        return cache[file_path]['encoding']

    # 如果缓存没有该文件或文件已更新，重新检测
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    # 更新缓存
    cache[file_path] = {'encoding': encoding, 'mtime': file_mtime}
    with open(CACHE_FILE, 'w', encoding='utf-8') as cache_file:
        json.dump(cache, cache_file, ensure_ascii=False, indent=4)

    print(f"检测到的编码: {encoding}")
    return encoding

encoding = get_file_encoding(file)

# 读取文本文件内容
def load_text():
    with open(file, encoding=encoding, errors='ignore') as f:
        lines = [line.strip() for line in f if line.strip()]  # 去掉空行
    return lines

# 初始化文本行
text_lines = load_text()
total_lines = len(text_lines)

# 动态计算 stepl 值
def calculate_stepl():
    char_width = text_font.measure("字")  # 每个字符的像素宽度
    window_width = root.winfo_width()
    return max(1, window_width // char_width)

# 分割文本为适合窗口大小的段落
def split_text_into_segments(line, stepl):
    segments = [line[i:i+stepl] for i in range(0, len(line), stepl)]
    return segments

# 更新显示文本
def display_text():
    global segment_index, text_segments
    stepl = calculate_stepl()  # 动态计算 stepl
    line = text_lines[row]
    text_segments = split_text_into_segments(line, stepl)  # 将当前行分割为多段
    segment_index = 0  # 重置段落索引
    show_segment()  # 显示第一段

# 显示当前段文本
def show_segment():
    if segment_index < len(text_segments):
        text_box.delete(1.0, tk.END)
        padded_segment = text_segments[segment_index].lstrip().rstrip("\n\r").ljust(calculate_stepl(), random.choice(chinese_fill_chars))
        text_box.insert(tk.END, padded_segment)

# 显示下一段或下一行文本
def display_next_segment_or_line():
    global segment_index, row
    if segment_index < len(text_segments) - 1:
        segment_index += 1  # 显示下一段
        show_segment()
    elif row < total_lines - 1:
        row += 1  # 显示下一行
        display_text()
        save_progress()

# 显示上一段或上一行文本
def display_previous_segment_or_line():
    global segment_index, row
    if segment_index > 0:
        segment_index -= 1  # 显示上一段
        show_segment()
    elif row > 0:
        row -= 1  # 显示上一行
        display_text()
        save_progress()

# 保存进度到 memo 文件
def save_progress():
    with open(file_memo, "w", encoding='utf-8') as f_memo:
        f_memo.write(str(row))

# 配置窗口
root = tk.Tk()
root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")  # 初始窗口大小
root.overrideredirect(True)  # 去掉标题栏和边框
root.attributes('-topmost', True)  # 窗口置顶
root.wm_attributes("-transparentcolor", "#F1F1F1")  # 设置黑色背景为透明

# 添加文本框，设置透明背景，文字白色
text_font = tkfont.Font(family=font_family, size=font_size)
text_box = tk.Text(root, wrap=tk.WORD, font=text_font, bg="#F1F1F1", fg="black", bd=0, highlightthickness=0)
text_box.pack(expand=True, fill="both")

# 设置字体大小的更新函数
def update_font_size(delta):
    global font_size
    font_size = max(6, font_size + delta)  # 保证字体不会小于6
    text_font.config(size=font_size)  # 更新字体大小
    display_text()  # 调整字体大小后重新显示文本



# 监听窗口大小改变事件
def on_resize(event):
    display_text()  # 调整窗口大小后重新显示文本

text_box.bind("<Configure>", on_resize)

# 鼠标右键按下以移动窗口
def on_mouse_drag(event):
    x = root.winfo_pointerx() - root._offset_x
    y = root.winfo_pointery() - root._offset_y
    root.geometry(f'+{x}+{y}')

def on_mouse_click(event):
    root._offset_x = event.x
    root._offset_y = event.y

text_box.bind("<Button-3>", on_mouse_click)  # 鼠标右键按下，准备拖动
text_box.bind("<B3-Motion>", on_mouse_drag)  # 鼠标右键拖动

# 保存键盘和鼠标的监控状态
is_monitoring_active = True  # 是否启用监控的标志

# 保存所有键盘监控的热键
monitored_keys = {
    'down': display_next_segment_or_line,   # 下键显示下一段或下一行
    'up': display_previous_segment_or_line,  # 上键显示上一段或上一行
    'alt+up': lambda: update_font_size(1),  # 增大字体
    'alt+down': lambda: update_font_size(-1),  # 减小字体
}

# 鼠标监控的句柄
mouse_hook = None

# 启用鼠标监控
def start_mouse_monitoring():
    global mouse_hook
    if not mouse_hook:  # 防止重复绑定
        mouse_hook = mouse.on_click(display_next_segment_or_line)
        print("鼠标监控已启用")

# 停止鼠标监控
def stop_mouse_monitoring():
    global mouse_hook
    if mouse_hook:
        mouse.unhook(mouse_hook)
        mouse_hook = None
        print("鼠标监控已暂停")

# 启用键盘监控
def start_keyboard_monitoring():
    for key, action in monitored_keys.items():
        keyboard.add_hotkey(key, action)
    print("键盘监控已启用")

# 停止键盘监控
def stop_keyboard_monitoring():
    for key in monitored_keys.keys():
        keyboard.remove_hotkey(key)
    print("键盘监控已暂停")

# 启用所有监控
def start_all_monitoring():
    global is_monitoring_active
    is_monitoring_active = True
    start_mouse_monitoring()
    start_keyboard_monitoring()
    print("所有监控已启用")

# 停止所有监控
def stop_all_monitoring():
    global is_monitoring_active
    is_monitoring_active = False
    stop_mouse_monitoring()
    stop_keyboard_monitoring()
    print("所有监控已暂停")

# 切换所有监控状态
def toggle_all_monitoring():
    if is_monitoring_active:
        stop_all_monitoring()
    else:
        start_all_monitoring()

# 添加 Ctrl+Alt 热键，用于切换所有监控状态
keyboard.add_hotkey('ctrl+alt', toggle_all_monitoring)

# 启动时启用所有监控
start_all_monitoring()


# 实现鼠标中键调整窗口大小功能
resizing = False

def start_resize(event):
    global resizing
    resizing = True
    root._resize_x = event.x
    root._resize_y = event.y
    root._width = root.winfo_width()
    root._height = root.winfo_height()

def stop_resize(event):
    global resizing
    resizing = False

def perform_resize(event):
    if resizing:
        delta_x = event.x - root._resize_x
        delta_y = event.y - root._resize_y
        new_width = max(200, root._width + delta_x)  # 设置最小宽度
        new_height = max(100, root._height + delta_y)  # 设置最小高度
        root.geometry(f"{new_width}x{new_height}")

# 将调整大小的事件绑定到鼠标中键
text_box.bind("<Button-2>", start_resize)  # 中键按下开始调整
text_box.bind("<B2-Motion>", perform_resize)  # 中键拖动调整大小
text_box.bind("<ButtonRelease-2>", stop_resize)  # 中键释放停止调整

# 读取上次保存的进度
if os.path.exists(file_memo):
    with open(file_memo, encoding=code) as f_memo:
        saved_row = f_memo.readline().strip()
        if saved_row.isdigit():
            row = int(saved_row)

def detect_and_update_styles():
    try:
        # 获取窗口位置
        x1 = root.winfo_rootx()
        y1 = root.winfo_rooty()


        # 截取窗口外的屏幕图像
        screenshot = ImageGrab.grab(bbox=(x1, y1, x1+5, y1+5))

        # 获取中间点的像素颜色
        middle_pixel = screenshot.getpixel((1,1))
        color_hex = f"#{middle_pixel[0]:02x}{middle_pixel[1]:02x}{middle_pixel[2]:02x}"

        # 更新背景颜色
        text_box.config(bg=color_hex)
        root.wm_attributes("-transparentcolor", color_hex)

        # 根据背景颜色调整字体颜色（黑白对比）
        luminance = (0.299 * middle_pixel[0] + 0.587 * middle_pixel[1] + 0.114 * middle_pixel[2]) / 255
        font_color = "black" if luminance > 0.5 else "white"  # 浅色背景用黑字，深色背景用白字
        text_box.config(fg=font_color)

    except Exception as e:
        print("检测或更新样式时出错:", e)

# 定时检测并更新 text_box 样式
def periodic_style_update():
    detect_and_update_styles()
    root.after(500, periodic_style_update)  # 每隔500毫秒检测一次

# 启动时调用
periodic_style_update()

# 启动时显示第一行
display_text()

# 通过ESC键退出
root.bind("<Escape>", lambda e: root.destroy())

root.mainloop()
