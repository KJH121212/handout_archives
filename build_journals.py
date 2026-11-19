import os
import json
import random
import string
import time
import urllib.parse
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 실제 배포되는 GitHub Pages 베이스 URL
GH_PAGES_BASE = "https://kjh121212.github.io/handout_archives"
OUTPUT_DIR = os.path.join(BASE_DIR, "fvtt_journals")
EXCLUDE_FILES = {"index.html"}

def gen_id():
    """FVTT 표준 16자리 랜덤 ID 생성"""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=16))

def clean_name(file_stem):
    """'handout_diary_01.html' -> 'Handout Diary 01' 형태로 정리 (취향에 따라 stem 그대로 써도 무방)"""
    return file_stem.replace("_", " ").strip()

def build_journals():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tree_data = defaultdict(list)

    # 폴더 순회 및 HTML 수집
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "fvtt_journals"]
        rel_dir = os.path.relpath(root, BASE_DIR)

        # 최상위 루트는 건너뛰고 하위 폴더만 처리 (필요시 포함 가능)
        if rel_dir == ".":
            continue

        for file in sorted(files):
            if file.endswith(".html") and file not in EXCLUDE_FILES:
                rel_file_path = os.path.join(rel_dir, file)
                
                # GitHub Pages URL 인코딩 생성
                url_path = "/".join([urllib.parse.quote(p) for p in rel_file_path.split(os.sep)])
                full_url = f"{GH_PAGES_BASE}/{url_path}"

                # 파일명(확장자 제외)을 페이지 이름으로 사용
                stem = os.path.splitext(file)[0]
                page_name = clean_name(stem)

                tree_data[rel_dir].append((page_name, full_url))

    now_ms = int(time.time() * 1000)

    # 폴더별로 Journal JSON 생성 (폴더 6개 -> JSON 6개)
    for folder_name, items in sorted(tree_data.items()):
        pages = []
        for i, (name, url) in enumerate(items):
            iframe_html = (
                f'<div style="width:100%;height:600px;position:relative;overflow:hidden;border-radius:6px;box-shadow:0 4px 15px rgba(0,0,0,0.5)">'
                f'<iframe src="{url}" style="position:absolute;top:0;left:0;width:100%;height:100%;border:none" sandbox="allow-scripts allow-forms"></iframe>'
                f'</div>'
            )
            pages.append({
                "sort": (i + 1) * 100000,
                "name": name,
                "type": "text",
                "_id": gen_id(),
                "system": {},
                "title": {"show": True, "level": 1},
                "image": {},
                "text": {"format": 1, "content": iframe_html},
                "video": {"controls": True, "volume": 0.5},
                "src": None,
                "category": None,
                "ownership": {"default": 0},
                "flags": {},
                "_stats": {
                    "coreVersion": "14.364",
                    "systemId": "CoC7",
                    "systemVersion": "8.15",
                    "createdTime": now_ms,
                    "modifiedTime": now_ms
                }
            })

        journal_json = {
            "name": folder_name, # 폴더 이름을 저널 이름으로 지정
            "pages": pages,
            "categories": [],
            "ownership": {"default": 0},
            "flags": {"core": {"locked": True}},
            "_stats": {
                "coreVersion": "14.364",
                "systemId": "CoC7",
                "systemVersion": "8.15",
                "createdTime": now_ms,
                "modifiedTime": now_ms
            }
        }

        # 파일명 생성: fvtt-JournalEntry-[폴더명].json
        safe_filename = folder_name.replace(os.sep, "_")
        output_file = os.path.join(OUTPUT_DIR, f"fvtt-JournalEntry-{safe_filename}.json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(journal_json, f, ensure_ascii=False, indent=2)

        print(f"-> 저널 JSON 생성: {safe_filename} ({len(pages)}개 페이지)")

    print(f"\n총 {len(tree_data)}개의 저널 파일이 '{OUTPUT_DIR}'에 생성되었습니다.")

if __name__ == "__main__":
    build_journals()