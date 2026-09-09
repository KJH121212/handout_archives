import os
import urllib.parse
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "index.html")
EXCLUDE_FILES = {"index.html"}

def build():
    tree_data = defaultdict(list)

    for root, dirs, files in os.walk(BASE_DIR):
        # .git, .venv 등 숨김 폴더 제외
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        rel_dir = os.path.relpath(root, BASE_DIR)
        
        for file in sorted(files):
            if file.endswith(".html") and file not in EXCLUDE_FILES:
                category = "루트" if rel_dir == "." else rel_dir
                # 브라우저용 URL 상대 경로 생성 (한글/공백 안전 인코딩)
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
    .container {{ max-width: 960px; margin: 0 auto; }}
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
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🎲 TRPG 인터랙티브 허브</h1>
      <span style="color: #8b949e; font-size: 0.85rem;">총 {total_count}개 파일</span>
    </header>
    <div class="grid">
{rendered_cards}
    </div>
  </div>
</body>
</html>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"-> index.html 생성 완료 (총 {total_count}개 HTML 파일 등록됨)")

if __name__ == "__main__":
    build()