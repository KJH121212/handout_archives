import os
import urllib.parse
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "index.html")
EXCLUDE_FILES = {"index.html"}


def build():
    # top_group -> sub_group ("" for direct files) -> list of (filename, encoded_url)
    grouped = defaultdict(lambda: defaultdict(list))

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        rel_dir = os.path.relpath(root, BASE_DIR)

        for file in sorted(files):
            if file.endswith(".html") and file not in EXCLUDE_FILES:
                rel_file_path = os.path.join(rel_dir, file) if rel_dir != "." else file
                encoded_path = "./" + "/".join(
                    urllib.parse.quote(p) for p in rel_file_path.split(os.sep)
                )
                if rel_dir == ".":
                    top_group, sub_group = "루트", ""
                else:
                    parts = rel_dir.split(os.sep)
                    top_group = parts[0]
                    sub_group = "/".join(parts[1:]) if len(parts) > 1 else ""
                grouped[top_group][sub_group].append((file, encoded_path))

    sections_html = []
    total_count = 0

    for top_group in sorted(grouped.keys()):
        sub_map = grouped[top_group]
        group_count = sum(len(v) for v in sub_map.values())
        total_count += group_count
        sub_keys = sorted(sub_map.keys())
        has_subgroups = any(k != "" for k in sub_keys)

        body_parts = []
        if has_subgroups:
            # Direct files under top_group (if any)
            if "" in sub_map:
                items_html = "\n".join(
                    f'''            <li data-search="{top_group.lower()} {fname.lower()}">
              <a href="{url}" target="_blank">
                <span class="file-name">📄 {fname}</span>
                <span class="btn">열기 ↗</span>
              </a>
            </li>'''
                    for fname, url in sub_map[""]
                )
                body_parts.append(f'          <ul class="link-list">\n{items_html}\n          </ul>')

            # Nested scenario subgroups
            for sub in sub_keys:
                if sub == "":
                    continue
                items = sub_map[sub]
                items_html = "\n".join(
                    f'''              <li data-search="{top_group.lower()} {sub.lower()} {fname.lower()}">
                <a href="{url}" target="_blank">
                  <span class="file-name">📄 {fname}</span>
                  <span class="btn">열기 ↗</span>
                </a>
              </li>'''
                    for fname, url in items
                )
                body_parts.append(f'''          <details class="subgroup" data-search-group="{top_group.lower()} {sub.lower()}">
            <summary class="subgroup-title">
              <span class="title-left"><span class="chevron">▸</span> 📂 {sub}</span>
              <span class="count">{len(items)}</span>
            </summary>
            <ul class="link-list">
{items_html}
            </ul>
          </details>''')
        else:
            items = sub_map[""]
            items_html = "\n".join(
                f'''          <li data-search="{top_group.lower()} {fname.lower()}">
            <a href="{url}" target="_blank">
              <span class="file-name">📄 {fname}</span>
              <span class="btn">열기 ↗</span>
            </a>
          </li>'''
                for fname, url in items
            )
            body_parts.append(f'        <ul class="link-list">\n{items_html}\n        </ul>')

        inner_html = "\n".join(body_parts)
        sub_meta = (
            f"{len([k for k in sub_keys if k != ''])}개 시나리오 · {group_count}개"
            if has_subgroups
            else f"{group_count}개"
        )

        sections_html.append(f'''      <details class="group" data-search-group="{top_group.lower()}">
        <summary class="group-title">
          <span class="title-left"><span class="chevron">▸</span> 📁 {top_group}</span>
          <span class="count">{sub_meta}</span>
        </summary>
        <div class="group-body">
{inner_html}
        </div>
      </details>''')

    rendered_sections = "\n".join(sections_html)

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TRPG 핸드아웃 허브</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      background: #121314;
      color: #f0f2f5;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      padding: 1.25rem;
      margin: 0;
    }}
    .container {{ max-width: 820px; margin: 0 auto; display: none; }}

    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
      border-bottom: 1px solid #33373b;
      padding-bottom: 0.75rem;
      margin-bottom: 0.85rem;
    }}
    h1 {{ margin: 0; font-size: 1.3rem; }}
    .total-badge {{ color: #8b949e; font-size: 0.82rem; }}

    /* 상단 검색 + 전체 접기/펼치기 바 */
    .toolbar {{
      display: flex;
      gap: 0.5rem;
      align-items: center;
      margin-bottom: 0.9rem;
      flex-wrap: wrap;
    }}
    .search-input {{
      flex: 1;
      min-width: 180px;
      padding: 0.45rem 0.7rem;
      border-radius: 6px;
      border: 1px solid #33373b;
      background: #0d1117;
      color: #f0f2f5;
      font-size: 0.86rem;
      outline: none;
    }}
    .search-input:focus {{ border-color: #58a6ff; }}
    .toolbar-btn {{
      padding: 0.45rem 0.75rem;
      border-radius: 6px;
      border: 1px solid #33373b;
      background: #1c1e20;
      color: #c9d1d9;
      font-size: 0.8rem;
      cursor: pointer;
      white-space: nowrap;
    }}
    .toolbar-btn:hover {{ background: #26292c; color: #fff; border-color: #58a6ff; }}

    /* 컴팩트 아코디언 목록 */
    .accordion-list {{
      display: flex;
      flex-direction: column;
      gap: 0.45rem;
    }}

    details.group {{
      background: #1c1e20;
      border: 1px solid #30343a;
      border-radius: 7px;
      overflow: hidden;
    }}
    details.group[open] {{ border-color: #444a52; }}

    summary {{
      list-style: none;
      cursor: pointer;
      user-select: none;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 0.5rem;
    }}
    summary::-webkit-details-marker {{ display: none; }}

    .group-title {{
      padding: 0.6rem 0.9rem;
      font-weight: 600;
      font-size: 0.92rem;
      background: #222529;
      transition: background 0.15s;
    }}
    .group-title:hover {{ background: #2a2e33; }}

    .title-left {{
      display: flex;
      align-items: center;
      gap: 0.45rem;
      min-width: 0;
      word-break: break-all;
    }}
    .chevron {{
      display: inline-block;
      font-size: 0.8rem;
      color: #8b949e;
      transition: transform 0.15s ease;
      width: 0.9rem;
      text-align: center;
      flex-shrink: 0;
    }}
    details[open] > summary .chevron {{
      transform: rotate(90deg);
      color: #58a6ff;
    }}

    .count {{
      font-size: 0.75rem;
      color: #8b949e;
      background: rgba(255, 255, 255, 0.05);
      padding: 2px 7px;
      border-radius: 999px;
      flex-shrink: 0;
      font-weight: 500;
    }}

    .group-body {{
      padding: 0.4rem 0.55rem 0.55rem;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      border-top: 1px solid #2c3035;
    }}

    /* 중첩 시나리오 아코디언 */
    details.subgroup {{
      background: #16181a;
      border: 1px solid #2b2f35;
      border-radius: 5px;
      overflow: hidden;
    }}
    .subgroup-title {{
      padding: 0.45rem 0.75rem;
      font-size: 0.86rem;
      font-weight: 600;
      color: #d8dee4;
      background: #1b1e22;
    }}
    .subgroup-title:hover {{ background: #24282e; }}

    .link-list {{
      list-style: none;
      margin: 0;
      padding: 0.3rem 0.4rem;
      display: flex;
      flex-direction: column;
      gap: 0.22rem;
    }}
    .link-list li a {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.36rem 0.6rem;
      border-radius: 4px;
      color: #dbe1e8;
      text-decoration: none;
      font-size: 0.84rem;
      background: rgba(255, 255, 255, 0.02);
      transition: background 0.12s, color 0.12s;
    }}
    .link-list li a:hover {{
      background: rgba(88, 166, 255, 0.14);
      color: #58a6ff;
    }}
    .file-name {{ word-break: break-all; }}
    .btn {{
      font-size: 0.72rem;
      background: #238636;
      color: #fff;
      padding: 1px 6px;
      border-radius: 4px;
      margin-left: 0.5rem;
      flex-shrink: 0;
    }}

    .empty-msg {{
      display: none;
      text-align: center;
      color: #8b949e;
      font-size: 0.88rem;
      padding: 2rem 1rem;
    }}

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
      width: 100%; padding: 0.6rem; border-radius: 4px;
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
      <h1>🎲 TRPG 핸드아웃 허브</h1>
      <span class="total-badge">총 {total_count}개 파일</span>
    </header>

    <div class="toolbar">
      <input type="search" id="search-input" class="search-input" placeholder="🔍 시나리오 또는 파일명 검색...">
      <button type="button" class="toolbar-btn" onclick="toggleAll(true)">모두 펼치기</button>
      <button type="button" class="toolbar-btn" onclick="toggleAll(false)">모두 접기</button>
    </div>

    <div class="accordion-list" id="accordion-list">
{rendered_sections}
    </div>
    <div class="empty-msg" id="empty-msg">검색 결과가 없습니다.</div>
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

    function toggleAll(openState) {{
      document.querySelectorAll("#accordion-list details").forEach(function(d) {{
        if (d.style.display !== "none") d.open = openState;
      }});
    }}

    document.getElementById("search-input").addEventListener("input", function(e) {{
      const q = e.target.value.trim().toLowerCase();
      const groups = document.querySelectorAll("#accordion-list > details.group");
      let anyVisible = false;

      groups.forEach(function(group) {{
        const items = group.querySelectorAll("li[data-search]");
        let groupMatch = 0;

        items.forEach(function(li) {{
          const hit = !q || li.getAttribute("data-search").includes(q);
          li.style.display = hit ? "" : "none";
          if (hit) groupMatch++;
        }});

        group.querySelectorAll("details.subgroup").forEach(function(sub) {{
          const subHits = Array.from(sub.querySelectorAll("li[data-search]")).some(
            function(li) {{ return li.style.display !== "none"; }}
          );
          sub.style.display = subHits ? "" : "none";
          if (q && subHits) sub.open = true;
          if (!q) sub.open = false;
        }});

        group.style.display = groupMatch > 0 ? "" : "none";
        if (q && groupMatch > 0) group.open = true;
        if (!q) group.open = false;
        if (groupMatch > 0) anyVisible = true;
      }});

      document.getElementById("empty-msg").style.display = anyVisible ? "none" : "block";
    }});
  </script>
</body>
</html>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"-> index.html 생성 완료 (총 {total_count}개 HTML 파일 등록됨)")


if __name__ == "__main__":
    build()
