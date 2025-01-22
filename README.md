# Moyu-Reader 🕶️

一个专为上班族设计的隐蔽小说阅读器，支持自适应窗口、快捷键操作、自动保存进度，让你安心摸鱼！

## 主要功能

- **无边框透明窗口** - 完美融入任意背景
- **智能文本分段** - 根据窗口宽度自动换行
- 🎨 背景颜色检测 - 自动调整文字颜色（黑/白）
- 📌 窗口置顶 & 自由拖拽
- 🖱️ 支持鼠标/键盘双操作
- ⚙️ 实时保存阅读进度
- 🔄 动态字体大小调整
- 📐 鼠标中键自由缩放窗口

## 配置文件说明 (config.json)

| 参数名称             | 类型    | 默认值               | 必填 | 描述                                 | 示例/建议值                     |
|----------------------|---------|----------------------|------|--------------------------------------|---------------------------------|
| `file_path`          | String  | `"novel.txt"`        | 是   | 小说文本文件路径（相对/绝对路径）    | `"C:\\books\\story.txt"`        |
| `chinese_fill_chars` | Array   | `["★", "☆", "※"]`   | 否   | 段落末尾填充字符（至少1个中文字符）  | `["❤", "·", "※"]`              |
| `font_family`        | String  | `"微软雅黑"`         | 否   | 显示字体（需系统支持）               | `"宋体"`, `"Consolas"`          |
| `font_size`          | Integer | `16`                 | 否   | 基础字号（范围6-36）                 | `12`（小屏）, `20`（高分屏）    |
| `window_width`       | Integer | `400`                | 否   | 窗口初始宽度（像素，最小值200）      | `500`（宽屏）, `300`（竖排）    |
| `window_height`      | Integer | `100`                | 否   | 窗口初始高度（像素，最小值50）       | `150`（双行）, `200`（多行）    |
| `window_x`           | Integer | `100`                | 否   | 窗口X坐标（屏幕左起像素）            | `屏幕宽度 - 450`（靠右定位）    |
| `window_y`           | Integer | `100`                | 否   | 窗口Y坐标（屏幕顶起像素）            | `屏幕高度 - 120`（底部悬浮）    |
| `code`               | String  | `"utf-8"`            | 否   | 文本文件编码格式                     | `"gbk"`, `"utf-8-sig"`          |

### 使用建议
1. **路径配置**  
   - 推荐使用相对路径（如`"novel.txt"`），便于项目移植
   - 复杂路径需双反斜杠转义：`"C:\\Users\\novel.txt"`



## 快捷键操作表

| 按键组合/操作          | 功能描述                  |
|-----------------------|--------------------------|
| ↑                     | 显示上一段落/上一行       |
| ↓                     | 显示下一段落/下一行       |
| Alt + ↑               | 增大字体字号              |
| Alt + ↓               | 减小字体字号              |
| 鼠标右键 + 拖动        | 自由拖拽窗口位置          |
| 鼠标中键 + 拖动        | 动态调整窗口尺寸          |
| 鼠标左键单击          | 快速跳转至下一段落        |
| Ctrl + Alt            | 启用/禁用键鼠监控         |
| Esc                   | 安全退出程序              |




## 注意事项

推荐在Windows系统下使用

初次打开时自动识别小说文本编码并记录到json文件中，防止txt文本乱码的情况

窗口透明度依赖系统支持

鼠标操作可能需要管理员权限
