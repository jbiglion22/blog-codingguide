# 수시 추합 시기 글의 본문·댓글을 받아 JSON으로 저장한다.
# 사용: python -I 도구/수시추합_본문댓글수집.py 임시폴더/posts.json 임시폴더/pages.json
# (posts.json은 도구/수시추합_수집.py 결과. 이미 받은 글은 건너뛰므로 중간에 멈춰도 다시 실행하면 이어서 받는다.)
# 작성자 닉네임·프로필은 저장하지 않는다. bs4(beautifulsoup4) 필요.
import json, re, sys, time, os, urllib.request
from bs4 import BeautifulSoup
SRC, OUT = sys.argv[1], sys.argv[2]
JEONG = re.compile(r"정시|진학사|점공|[가나다]군|낙지|모의지원|표본|환산|\d칸|칸수|백분위|표점")
SUSI = re.compile(r"수시|학종|교과|논술|학추|면접|예비|전화|추추|조기발표|조발|최초합|6광|광탈|학생부")
def year_of(dt):
    y, m = int(dt[:4]), int(dt[5:7]); return y + 1 if m >= 11 else y
def keep(p):
    if not p["dt"]: return False
    y = year_of(p["dt"])
    if not (f"{y-1}-11-20" <= p["dt"][:10] <= f"{y}-01-10"): return False
    t = p["title"] + " " + p["content"]
    return not (JEONG.search(t) and not SUSI.search(t))
posts = [p for p in json.load(open(SRC, encoding="utf-8")) if keep(p)]
done = {}
if os.path.exists(OUT):
    done = {d["id"]: d for d in json.load(open(OUT, encoding="utf-8"))}
def fetch(pid):
    req = urllib.request.Request("https://orbi.kr/" + pid.zfill(11), headers={"User-Agent": "Mozilla/5.0"})
    for _ in range(3):
        try: return urllib.request.urlopen(req, timeout=20).read()
        except Exception: time.sleep(2)
    return None
n = 0
for p in posts:
    if p["id"] in done: continue
    raw = fetch(p["id"])
    if raw is None: continue
    s = BeautifulSoup(raw, "html.parser")
    body = s.select_one(".content-wrap")
    comments = []
    for li in s.select("li.comment"):
        tx = li.select_one(".comment-text")
        if not tx: continue
        dep = li.select_one(".depth")
        m = re.search(r"margin-left:\s*(\d+)", dep.get("style", "")) if dep else None
        comments.append({"text": re.sub(r"\s+", " ", tx.get_text(" ", strip=True)), "reply": bool(m and int(m.group(1)) > 0)})
    done[p["id"]] = {**p, "body": re.sub(r"\s+", " ", body.get_text(" ", strip=True))[:4000] if body else "", "comments": comments}
    n += 1
    if n % 50 == 0:
        json.dump(list(done.values()), open(OUT, "w", encoding="utf-8"), ensure_ascii=False); print(n, len(done), flush=True)
    time.sleep(0.4)
json.dump(list(done.values()), open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("saved", len(done), "of", len(posts))
