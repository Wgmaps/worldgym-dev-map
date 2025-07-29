import os

# 所有資料夾
folders = sorted([f for f in os.listdir() if f.startswith('2025-') and os.path.isdir(f)])

# 對應標題格式（未來可調整）
def format_title(folder):
    return f"🦍🌍 WorldGym HZ 每日開發地圖 {folder} 💰"

html_head = '''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>WorldGym HZ 地圖首頁</title>
    <style>
        body { font-family: "Segoe UI", sans-serif; padding: 40px; }
        h1 { font-size: 26px; }
        ul { list-style-type: none; padding-left: 0; }
        li { margin: 10px 0; }
        a { text-decoration: none; color: #1a73e8; font-size: 18px; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>🦍🌍 WorldGym HZ 地圖首頁</h1>
    <ul>
'''

html_body = ""
for folder in folders:
    title = format_title(folder)
    html_body += f'        <li><a href="{folder}/index.html">{title}</a></li>\n'

html_tail = '''    </ul>
</body>
</html>
'''

# 合併並儲存
full_html = html_head + html_body + html_tail
Path("index.html").write_text(full_html, encoding="utf-8")
print("✅ 已產生首頁 index.html")
