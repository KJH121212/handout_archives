from pathlib import Path
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent

def convert_images_to_webp():
    png_files = list(ROOT_DIR.rglob("*.png"))
    print(f"[1/2] PNG -> WebP 변환 시작 (총 {len(png_files)}개)")

    for png_path in png_files:
        webp_path = png_path.with_suffix(".webp")
        try:
            with Image.open(png_path) as img:
                # RGBA 투명도 보존 변환
                img.save(webp_path, "WEBP", quality=90)
            png_path.unlink()  # 원본 PNG 삭제
            print(f"  변환 완료: {png_path.name} -> {webp_path.name}")
        except Exception as e:
            print(f"  실패 ({png_path}): {e}")

def update_html_references():
    html_files = list(ROOT_DIR.rglob("*.html"))
    print(f"\n[2/2] HTML 파일 내부 .png -> .webp 치환 시작 (총 {len(html_files)}개)")

    for html_path in html_files:
        try:
            content = html_path.read_text(encoding="utf-8")
            if ".png" in content or ".PNG" in content:
                new_content = content.replace(".png", ".webp").replace(".PNG", ".webp")
                html_path.write_text(new_content, encoding="utf-8")
                print(f"  경로 수정 완료: {html_path.relative_to(ROOT_DIR)}")
        except Exception as e:
            print(f"  치환 실패 ({html_path}): {e}")

if __name__ == "__main__":
    convert_images_to_webp()
    update_html_references()
    print("\n모든 작업이 완료되었습니다.")