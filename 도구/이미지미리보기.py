"""네이버 글 index.html의 빨간 이미지 표시 위에 이미지 미리보기를 넣는다.

사용법:  python 도구/이미지미리보기.py 문서/네이버-코딩가이드/<글폴더>/index.html

- 빨간 글씨 [[ 이미지: 제목 (파일명) ]] 바로 위에 그 이미지를 넣는다.
- 이미지를 HTML 안에 직접(data URI) 넣으므로 어떤 창에서 열어도 보인다.
  (Claude 앱의 브라우저 창은 로컬 파일을 data: 주소로 열어서 images/ 상대 경로 그림이 보이지 않는다.)
- 용량을 줄이려고 폭 720px JPEG로 줄여서 넣는다. 원본 이미지 파일은 건드리지 않는다.
- 아직 images/에 없는 파일은 미리보기를 넣지 않는다. 이미지가 새로 들어오면 다시 실행한다.
- 여러 번 실행해도 된다. 앞서 넣은 미리보기(data-preview)는 지우고 새로 넣는다.
- 필요 패키지: Pillow
"""
import base64, io, os, re, sys
from PIL import Image

WIDTH = 720
RED = re.compile(r'<p style="color:#e60000;font-weight:bold;">\[\[ 이미지: [^\]]*?\(([^()]+\.(?:png|jpg|jpeg))\) \]\]</p>')
OLD = re.compile(r'<p data-preview="1"[^>]*>.*?</p>\n|<p style="margin:0;"><img src="images/[^"]*"[^>]*></p>\n', re.S)


def preview(path):
    im = Image.open(path).convert("RGB")
    if im.width > WIDTH:
        im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main(html_path):
    folder = os.path.dirname(os.path.abspath(html_path))
    s = open(html_path, encoding="utf-8").read()
    s = OLD.sub("", s)
    shown, missing = [], []

    def rep(m):
        name = m.group(1)
        img = os.path.join(folder, "images", name)
        if not os.path.exists(img):
            missing.append(name)
            return m.group(0)
        shown.append(name)
        return (f'<p data-preview="1" style="margin:0;"><img src="{preview(img)}" alt="" '
                f'style="max-width:100%;display:block;"></p>\n' + m.group(0))

    s = RED.sub(rep, s)
    open(html_path, "w", encoding="utf-8").write(s)
    print("미리보기 넣음:", len(shown), shown)
    print("아직 없는 이미지:", len(missing), missing)


if __name__ == "__main__":
    main(sys.argv[1])
