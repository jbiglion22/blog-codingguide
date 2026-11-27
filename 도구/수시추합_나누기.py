import json, re, os, sys, shutil
from collections import defaultdict, Counter
SRC, OUT = sys.argv[1], sys.argv[2]
posts = json.load(open(SRC, encoding="utf-8"))

SCHOOLS = [
 ("서울대", r"서울대(?!입)|설대|서울대학교"), ("연세대", r"연세대|연대(?!기|표)|연세"), ("고려대", r"고려대|고대(?!사|로)"),
 ("서강대", r"서강"), ("성균관대", r"성균관|성대(?!하)"), ("한양대", r"한양대|한양|냥대"),
 ("중앙대", r"중앙대|중대(?!형|한|하|사|성|재)"), ("경희대", r"경희"), ("한국외대", r"외대|한국외"),
 ("서울시립대", r"시립대"), ("이화여대", r"이화|이대(?!로|론|비|상)"), ("건국대", r"건국|건대"),
 ("동국대", r"동국"), ("홍익대", r"홍익|홍대"), ("숙명여대", r"숙명|숙대"),
 ("국민대", r"국민대"), ("숭실대", r"숭실"), ("세종대", r"세종대"), ("단국대", r"단국|단대"),
 ("광운대", r"광운"), ("명지대", r"명지"), ("상명대", r"상명"), ("가천대", r"가천"),
 ("인하대", r"인하대|인하(?!여|게)"), ("아주대", r"아주대"), ("인천대", r"인천대"), ("경기대", r"경기대"),
 ("서울과기대", r"서울과기|과기대"), ("한국항공대", r"항공대"), ("성신여대", r"성신"),
 ("동덕여대", r"동덕"), ("덕성여대", r"덕성"), ("서울여대", r"서울여대"), ("한성대", r"한성대"),
 ("서경대", r"서경대"), ("삼육대", r"삼육"), ("가톨릭대", r"가톨릭"),
 ("부산대", r"부산대"), ("경북대", r"경북대"), ("전남대", r"전남대"), ("전북대", r"전북대"),
 ("충남대", r"충남대"), ("충북대", r"충북대"), ("강원대", r"강원대"), ("경상국립대", r"경상국립|경상대"),
 ("부경대", r"부경대"), ("제주대", r"제주대"), ("울산대", r"울산대"), ("영남대", r"영남대"),
 ("계명대", r"계명"), ("조선대", r"조선대"), ("한림대", r"한림"), ("순천향대", r"순천향"),
 ("수원대", r"수원대"), ("한국교원대", r"교원대"), ("교육대학", r"교대(?!생|로)|교육대"),
 ("KAIST", r"카이스트|KAIST|kaist"), ("포스텍", r"포스텍|포항공대|POSTECH"), ("UNIST", r"유니스트|UNIST"),
 ("GIST", r"지스트|GIST"), ("DGIST", r"디지스트|DGIST"), ("한국예술종합학교", r"한예종"),
 ("경찰대", r"경찰대"), ("사관학교", r"사관학교|육사|공사(?!항)|해사"),
]
SCH = [(n, re.compile(p)) for n, p in SCHOOLS]
JEONG = re.compile(r"정시|진학사|점공|[가나다]군|낙지|모의지원|표본|환산|\d칸|칸수|백분위|표점")
SUSI = re.compile(r"수시|학종|교과|논술|학추|면접|예비|전화|추추|조기발표|조발|최초합|6광|광탈|학생부")
TAGS = [
 ("전화", r"전화|전추"), ("못받음·부재중", r"못\s?받|부재중|놓쳤|놓침"),
 ("몇 번까지·가능성", r"몇\s?번|몇번까지|돌까|빠질까|가능성|확률|될까|되나요|될까요"),
 ("예비번호", r"예비"), ("등록·포기·환불", r"포기|예치금|환불|등록금|등록"),
 ("추추합·마지막날", r"추추|마지막\s?날|막날|막차"), ("홈페이지·문자", r"홈페이지|조회|문자"),
 ("합격 소식", r"붙었|합격했|됐어요|됐습니다|떴어|떴다|성공"), ("불합·탈락", r"떨어|불합|탈락|광탈"),
 ("어디 갈까", r"고민|vs|VS|어디\s?가|둘\s?중"), ("불안·멘탈", r"제발|희망고문|멘탈|불안|미치|ㅠ"),
]
TAGS = [(n, re.compile(p)) for n, p in TAGS]

def year_of(dt):
    y, m = int(dt[:4]), int(dt[5:7])
    return y + 1 if m >= 11 else y
def in_season(dt, y):
    return f"{y-1}-11-20" <= dt[:10] <= f"{y}-01-10"

byyear = defaultdict(lambda: defaultdict(list)); stats = defaultdict(Counter); kept = Counter(); dropped = Counter()
for p in posts:
    dt = p["dt"]
    if not dt: continue
    y = year_of(dt)
    if not in_season(dt, y): continue
    txt = p["title"] + " " + p["content"]
    if JEONG.search(txt) and not SUSI.search(txt):
        dropped[y] += 1; continue
    kept[y] += 1
    p["tags"] = [n for n, r in TAGS if r.search(txt)]
    for t in p["tags"]: stats[y][t] += 1
    names = sorted({n for n, r in SCH if r.search(txt)})
    for n in names or ["학교미상"]:
        byyear[y][n].append(p)

# 학교별 폴더 / 학년도별 파일
NL = "\n"
if os.path.isdir(OUT):
    for d in os.listdir(OUT):
        full = os.path.join(OUT, d)
        if os.path.isdir(full): shutil.rmtree(full)
        elif d in ("학년도별_요약.md", "학교목록.md"): os.remove(full)
os.makedirs(OUT, exist_ok=True)
def line(p):
    c = p["content"][:150] + ("…" if len(p["content"]) > 150 else "")
    tg = " `" + "·".join(p["tags"]) + "`" if p["tags"] else ""
    head = f"- {p['dt'][:16]} · [{p['title'] or '(제목 없음)'}]({p['url']}){tg}"
    return head + NL + "  - " + c if c else head
years = sorted(byyear)
schools = defaultdict(dict)
for y in years:
    for name, ps in byyear[y].items(): schools[name][y] = sorted(ps, key=lambda x: x["dt"])
# 묶음: 네이버-코딩가이드-대학입시2027-연재.md의 '특수대학 목록'과 본교(본캠퍼스) 소재지 기준
SPECIAL = {"KAIST", "포스텍", "UNIST", "GIST", "DGIST", "사관학교", "경찰대", "한국예술종합학교", "교육대학", "한국교원대"}
SEOUL = {"서울대", "연세대", "고려대", "서강대", "성균관대", "한양대", "중앙대", "경희대", "한국외대", "서울시립대",
         "이화여대", "건국대", "동국대", "홍익대", "숙명여대", "국민대", "숭실대", "세종대", "광운대", "명지대",
         "상명대", "서울과기대", "성신여대", "동덕여대", "덕성여대", "서울여대", "한성대", "서경대", "삼육대"}
def group(n):
    if n == "학교미상": return ""
    return "특수학교" if n in SPECIAL else "서울지역" if n in SEOUL else "그외지역"
def rel(n):
    g = group(n); return f"{g}/{n}" if g else n
for name, ys in schools.items():
    d = os.path.join(OUT, rel(name)); os.makedirs(d, exist_ok=True)
    for y, ps in ys.items():
        with open(os.path.join(d, f"{y}학년도.md"), "w", encoding="utf-8") as f:
            f.write(f"# {name} · {y}학년도 수시 추가합격" + NL + NL)
            f.write("- 출처: 오르비(orbi.kr) 검색어 '추합' 결과의 제목·미리보기 글(본문 전체·작성자 닉네임은 저장하지 않음)" + NL)
            f.write(f"- 기간: {y-1}-11-20 ~ {y}-01-10 · 글 {len(ps)}편 · 한 글에 여러 학교가 나오면 각 학교 폴더에 모두 넣음" + NL)
            f.write("- 태그는 제목·미리보기의 낱말로 자동 분류한 것이라 정확하지 않을 수 있음" + NL + NL)
            f.write(NL.join(line(p) for p in ps) + NL)
order = sorted(schools, key=lambda n: (n == "학교미상", -sum(len(v) for v in schools[n].values())))
with open(os.path.join(OUT, "학교목록.md"), "w", encoding="utf-8") as f:
    f.write("# 학교별 글 수" + NL + NL + "- 한 글에 여러 학교가 나오면 각 학교에 모두 셈. 숫자를 누르면 그 학년도 파일이 열림" + NL)
    f.write("- 묶음: 서울지역(본교가 서울) · 특수학교(연재 파일의 특수대학 목록: 과학기술원·사관학교·경찰대·한예종·교육대학·교원대) · 그외지역" + NL)
    for g in ["서울지역", "특수학교", "그외지역", ""]:
        names = [n for n in order if group(n) == g]
        if not names: continue
        f.write(NL + "## " + (g or "학교미상") + NL + NL)
        f.write("| 학교 | " + " | ".join(f"{y}학년도" for y in years) + " | 합계 |" + NL + "|---|" + "---|" * (len(years) + 1) + NL)
        for n in names:
            cells = [f"[{len(schools[n][y])}]({rel(n)}/{y}학년도.md)" if y in schools[n] else "-" for y in years]
            f.write(f"| {n} | " + " | ".join(cells) + f" | {sum(len(v) for v in schools[n].values())} |" + NL)
with open(os.path.join(OUT, "학년도별_요약.md"), "w", encoding="utf-8") as f:
    f.write("# 학년도별 수시 추가합격 글 요약" + NL + NL + "| 학년도 | 수시 추합 시기 글 | 뺀 정시 글 |" + NL + "|---|---|---|" + NL)
    for y in years: f.write(f"| {y}학년도 ({y-1}-11-20 ~ {y}-01-10) | {kept[y]} | {dropped[y]} |" + NL)
    f.write(NL + "## 질문·이야기 유형(자동 분류, 한 글이 여러 유형에 들 수 있음)" + NL + NL)
    f.write("| 유형 | " + " | ".join(f"{y}학년도" for y in years) + " |" + NL + "|---|" + "---|" * len(years) + NL)
    for t, _ in TAGS: f.write(f"| {t} | " + " | ".join(str(stats[y][t]) for y in years) + " |" + NL)
print([(y, kept[y], dropped[y]) for y in years], len(schools))

# ---- 경험담 · 질문과 답변 (세 번째 인자로 도구/수시추합_본문댓글수집.py의 pages.json을 주면 만든다) ----
if len(sys.argv) > 3:
    pages = json.load(open(sys.argv[3], encoding="utf-8"))
    QTITLE = re.compile(r"\?|까요|나요|될까|되나|궁금|질문|인가요|있나|있을까|어떡|어떻게|ㄱㄴ|가능\??$")
    EXPW = re.compile(r"후기|받았|받음|받았어|왔어|왔습니다|왔다|왔음|왔네|됐어|됐습니다|됐다|됐음|됐네|붙었|붙음|떴어|떴다|떴습니다|떴네|합격했|합격입니다|ㅇㅈ|작년에|재작년|경험|했었|받아봄|받아봤|썰|돌았|빠졌|빠지고|끊겼")
    FIRST = re.compile(r"저는|제가|저도|저 |나도|내가|나는|본인|후기|ㅇㅈ|인증|친구|우리 ?애|아들|딸")
    CHUHAP = re.compile(r"추합|추가합격|충원|예비|추추|막차|전화")
    NOEXP = re.compile(r"칼럼|공부법|컨설팅|예측|분석|입결표|가이드|정리|이유|허와 실|빵꾸|vs|VS")
    CHEER = re.compile(r"추합\s?기원|기원합니다|기원해|화이팅|파이팅|축하|ㅊㅋ|부럽|가즈아|기도|응원|고생하셨|수고하셨")
    def meaningful(c):
        t = c["text"].strip()
        core = re.sub(r"[ㅋㅎㅠㅜ!?.~\s]", "", t)
        if len(core) < 25: return False
        if CHEER.search(t) and len(core) < 60: return False
        return True
    exp = defaultdict(lambda: defaultdict(list)); qa = defaultdict(lambda: defaultdict(list))
    ne = nq = 0
    for p in pages:
        y = year_of(p["dt"]); body = p.get("body", "")
        txt = p["title"] + " " + body[:400]
        names = sorted({n for n, r in SCH if r.search(txt)}) or ["학교미상"]
        good = [c for c in p.get("comments", []) if meaningful(c)]
        is_q = bool(QTITLE.search(p["title"])) or body.rstrip().endswith("?")
        full = p["title"] + " " + body
        if len(JEONG.findall(full)) >= 2 and not SUSI.search(full): continue  # 본문까지 보면 정시 이야기인 글
        head2 = p["title"] + " " + body[:500]
        exp_ok = (not is_q and EXPW.search(head2) and FIRST.search(head2) and CHUHAP.search(head2)
                  and not NOEXP.search(p["title"]) and len(JEONG.findall(head2)) < 2 and len(body) >= 10)
        if exp_ok:
            ne += 1
            for n in names: exp[n][y].append((p, good))
        elif good:
            nq += 1
            for n in names: qa[n][y].append((p, good))
    def block(p, good, kind):
        b = p.get("body", "")
        b = b[:600] + ("…" if len(b) > 600 else "")
        s = f"### {p['dt'][:16]} · [{p['title'] or '(제목 없음)'}]({p['url']})" + NL + NL + ("> " + b if b else "> (본문 없음)") + NL
        if good:
            s += NL + ("의미 있는 댓글:" if kind == "exp" else "답변(짧은 응원·한 줄 답은 뺌):") + NL
            for c in good[:8]:
                t = c["text"][:400] + ("…" if len(c["text"]) > 400 else "")
                s += ("  - ↳ " if c["reply"] else "- ") + t + NL
        return s
    head = {"exp": ("경험담", "추가합격을 직접 겪은 이야기(받은 때·예비번호가 움직인 과정·합격 뒤 이야기 등)로 보이는 글. 제목이 질문이 아닌 글 중 겪은 일을 나타내는 말이 든 것을 자동으로 고름"),
            "qa": ("질문과답변", "질문 글 가운데 길고 내용 있는 댓글(25자 이상, 짧은 응원·한 줄 답 제외)이 달린 것만 모음. 댓글은 개인 의견이라 틀릴 수 있음")}
    cnt = Counter()
    for kind, data in (("exp", exp), ("qa", qa)):
        title, desc = head[kind]
        for n, ys in data.items():
            d = os.path.join(OUT, rel(n)); os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, f"{title}.md"), "w", encoding="utf-8") as f:
                f.write(f"# {n} · 수시 추가합격 {title}" + NL + NL)
                f.write(f"- {desc}" + NL)
                f.write("- 출처: 오르비(orbi.kr). 본문은 앞 600자, 댓글은 400자까지. 작성자 닉네임은 저장하지 않음. 블로그에 문장을 옮기지 않고 흐름·유형 참고용으로만 씀" + NL)
                for y in sorted(ys):
                    f.write(NL + f"## {y}학년도 ({len(ys[y])}편)" + NL + NL)
                    f.write(NL.join(block(p, g, kind) for p, g in sorted(ys[y], key=lambda x: x[0]["dt"])))
                cnt[(kind, n)] = sum(len(v) for v in ys.values())
    with open(os.path.join(OUT, "학교목록.md"), "a", encoding="utf-8") as f:
        f.write(NL + "## 경험담·질문과답변 파일" + NL + NL + f"- 본문·댓글을 받은 글 {len(pages)}편 중 경험담 {ne}편, 의미 있는 답변이 달린 질문 {nq}편" + NL + NL)
        f.write("| 학교 | 경험담 | 질문과답변 |" + NL + "|---|---|---|" + NL)
        for n in order:
            e, q = cnt[("exp", n)], cnt[("qa", n)]
            if not (e or q): continue
            ce = f"[{e}]({rel(n)}/경험담.md)" if e else "-"; cq = f"[{q}]({rel(n)}/질문과답변.md)" if q else "-"
            f.write(f"| {n} | {ce} | {cq} |" + NL)
    print("경험담", ne, "질문과답변", nq)
