import urllib.request, urllib.parse, re, json, time, html, sys
OUT = sys.argv[1]
Q = "추합"
posts = {}
def get(p):
    url = "https://orbi.kr/search?q=" + urllib.parse.quote(Q) + "&type=keyword&page=" + str(p)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for _ in range(3):
        try:
            return urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
        except Exception:
            time.sleep(2)
    return ""
def strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).replace("\xa0", " ").strip()
last = "9999"
for p in range(1, 400):
    t = get(p)
    blocks = re.split(r'<li class="[^"]*" data-post-id="', t)[1:]
    if not blocks:
        print("end", p); break
    for b in blocks:
        pid = b.split('"', 1)[0]
        m = re.search(r'<abbr title="@([^"]+)"', b)
        dt = m.group(1) if m else ""
        tm = re.search(r'<p class="title">\s*<a[^>]*>(.*?)</a>', b, re.S)
        cm = re.search(r'<p class="content[^"]*">(.*?)</p>', b, re.S)
        title = re.sub(r"\s+", " ", strip(tm.group(1))) if tm else ""
        content = re.sub(r"\s+", " ", strip(cm.group(1))) if cm else ""
        posts[pid] = {"id": pid, "dt": dt, "title": title, "content": content,
                      "url": "https://orbi.kr/" + pid.zfill(11)}
        if dt: last = min(last, dt)
    if p % 20 == 0: print(p, len(posts), last, flush=True)
    if last < "2024-11-25": print("stop", p, last); break
    time.sleep(0.3)
json.dump(list(posts.values()), open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("saved", len(posts))
