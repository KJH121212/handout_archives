import os
import urllib.parse
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "index.html")
EXCLUDE_FILES = {"index.html"}

def build():
    tree_data = defaultdict(list)

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        rel_dir = os.path.relpath(root, BASE_DIR)
        
        for file in sorted(files):
            if file.endswith(".html") and file not in EXCLUDE_FILES:
                category = "루트" if rel_dir == "." else rel_dir
                rel_file_path = os.path.join(rel_dir, file) if rel_dir != "." else file
                encoded_path = "./" + "/".join([urllib.parse.quote(p) for p in rel_file_path.split(os.sep)])
                tree_data[category].append((file, encoded_path))

    cards_html = []
    for category in sorted(tree_data.keys()):
        items = tree_data[category]
        cards_html.append(f'''
    <div class="card">
      <div class="card-title">📁 {category} <span class="count">({len(items)})</span></div>
      <ul class="link-list">''')
        for fname, url in items:
            cards_html.append(f'''
        <li>
          <a href="{url}" target="_blank">
            <span class="file-name">{fname}</span>
            <span class="btn">열기 ↗</span>
          </a>
        </li>''')
        cards_html.append('''
      </ul>
    </div>''')

    rendered_cards = "\n".join(cards_html)
    total_count = sum(len(v) for v in tree_data.values())

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TRPG 핸드아웃 허브</title>
  <style>
    body {{ background: #121314; color: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; padding: 1.5rem; margin: 0; }}
    .container {{ max-width: 960px; margin: 0 auto; display: none; }}
    header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #33373b; padding-bottom: 1rem; margin-bottom: 1.5rem; }}
    h1 {{ margin: 0; font-size: 1.5rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1rem; }}
    .card {{ background: #1c1e20; border: 1px solid #33373b; border-radius: 8px; overflow: hidden; }}
    .card-title {{ background: #26292c; padding: 0.75rem 1rem; font-weight: bold; font-size: 0.95rem; border-bottom: 1px solid #33373b; }}
    .count {{ font-size: 0.8rem; color: #8b949e; }}
    .link-list {{ list-style: none; margin: 0; padding: 0.5rem; display: flex; flex-direction: column; gap: 0.4rem; }}
    .link-list li a {{ display: flex; justify-content: space-between; align-items: center; background: rgba(255, 255, 255, 0.03); padding: 0.5rem 0.75rem; border-radius: 4px; color: #f0f2f5; text-decoration: none; font-size: 0.9rem; }}
    .link-list li a:hover {{ background: rgba(88, 166, 255, 0.15); color: #58a6ff; }}
    .file-name {{ word-break: break-all; }}
    .btn {{ font-size: 0.75rem; background: #238636; color: #fff; padding: 2px 6px; border-radius: 4px; margin-left: 0.5rem; flex-shrink: 0; }}

    /* 잠금 화면 스타일 */
    #auth-overlay {{
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: #121314; display: flex; align-items: center; justify-content: center;
      z-index: 9999;
    }}
    .auth-box {{
      background: #1c1e20; border: 1px solid #33373b; padding: 2rem; border-radius: 8px;
      text-align: center; width: 280px; box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    }}
    .auth-box h2 {{ margin: 0 0 1rem; font-size: 1.1rem; color: #f0f2f5; }}
    .auth-box input {{
      width: 100%; box-sizing: border-box; padding: 0.6rem; border-radius: 4px;
      border: 1px solid #33373b; background: #0d1117; color: #fff; text-align: center;
      margin-bottom: 0.8rem; font-size: 1rem; outline: none;
    }}
    .auth-box input:focus {{ border-color: #58a6ff; }}
    .auth-box button {{
      width: 100%; padding: 0.6rem; border: none; border-radius: 4px;
      background: #238636; color: #fff; font-weight: bold; cursor: pointer;
    }}
    .auth-box button:hover {{ background: #2ea043; }}
    .error-msg {{ color: #f85149; font-size: 0.8rem; margin-top: 0.6rem; display: none; }}
  </style>
</head>
<body>
  <!-- 암호 입력 오버레이 -->
  <div id="auth-overlay">
    <div class="auth-box">
      <h2>🔒 접근 권한 확인</h2>
      <input type="password" id="pw-input" placeholder="암호 입력" autofocus>
      <button onclick="checkPassword()">인증</button>
      <div id="error-msg" class="error-msg">암호가 일치하지 않습니다.</div>
    </div>
  </div>

  <!-- 메인 허브 컨텐츠 -->
  <div class="container" id="hub-container">
    <header>
      <h1>🎲 TRPG 인터랙티브 허브</h1>
      <span style="color: #8b949e; font-size: 0.85rem;">총 {total_count}개 파일</span>
    </header>
    <div class="grid">
{rendered_cards}
    </div>
  </div>

  <script>
    const TARGET_PW = "KJH121212";

    function unlock() {{
      document.getElementById("auth-overlay").style.display = "none";
      document.getElementById("hub-container").style.display = "block";
    }}

    function checkPassword() {{
      const val = document.getElementById("pw-input").value;
      const errorEl = document.getElementById("error-msg");
      if (val === TARGET_PW) {{
        unlock();
      }} else {{
        errorEl.style.display = "block";
        document.getElementById("pw-input").value = "";
        document.getElementById("pw-input").focus();
      }}
    }}

    document.getElementById("pw-input").addEventListener("keydown", function(e) {{
      if (e.key === "Enter") checkPassword();
    }});
  </script>
</body>
</html>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"-> index.html 생성 완료 (총 {total_count}개 HTML 파일 등록됨)")

if __name__ == "__main__":
    build()