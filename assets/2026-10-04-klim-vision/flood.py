from collections import deque
W, H = 1152, 1536
data = open('img.bmp','rb').read()
raw = data[54:]
stride = (W*3 + 3) & ~3
gray = bytearray(W*H)
for y in range(H):
    row = raw[y*stride : y*stride + W*3]
    gray[y*W:(y+1)*W] = bytes((row[i+2]+row[i+1]+row[i])//3 for i in range(0, W*3, 3))

def analyze(name, x0, y0, x1, y1, thr=45, min_enc=30):
    w = x1-x0+1; h = y1-y0+1
    vals = [gray[(y0+dy)*W + x0+dx] for dy in range(h) for dx in range(w)]
    vals.sort()
    paper = vals[int(len(vals)*0.92)]
    ink = None
    for t in (thr, thr-10, thr-18):
        m = bytearray(w*h)
        for dy in range(h):
            for dx in range(w):
                if gray[(y0+dy)*W + x0+dx] < paper - t:
                    m[dy*w+dx] = 1
        if sum(m) >= 0.012*w*h:
            ink = m; break
    if ink is None: ink = bytearray(w*h)
    # flood fill background from bbox border
    seen = bytearray(w*h)
    q = deque()
    for x in range(w):
        for y in (0, h-1):
            if not ink[y*w+x] and not seen[y*w+x]:
                seen[y*w+x] = 1; q.append(y*w+x)
    for y in range(h):
        for x in (0, w-1):
            if not ink[y*w+x] and not seen[y*w+x]:
                seen[y*w+x] = 1; q.append(y*w+x)
    while q:
        p = q.popleft()
        px = p % w
        for np in (p-1 if px>0 else -1, p+1 if px<w-1 else -1,
                   p-w if p>=w else -1, p+w if p<w*(h-1) else -1):
            if np < 0: continue
            if not ink[np] and not seen[np]:
                seen[np] = 1; q.append(np)
    enclosed = [p for p in range(w*h) if not ink[p] and not seen[p]]
    # ink components inside bbox (dots)
    lab = [-1]*(w*h); comps = []
    for s in range(w*h):
        if ink[s] and lab[s] < 0:
            cid = len(comps); q = deque([s]); lab[s] = cid; pix = [s]
            while q:
                p = q.popleft(); px = p % w
                for np in (p-1 if px>0 else -1, p+1 if px<w-1 else -1,
                           p-w if p>=w else -1, p+w if p<w*(h-1) else -1):
                    if np < 0: continue
                    if ink[np] and lab[np] < 0:
                        lab[np] = cid; q.append(np); pix.append(np)
            comps.append(pix)
    dots = []
    for pix in comps:
        xs = [p % w for p in pix]; ys = [p // w for p in pix]
        bw = max(xs)-min(xs)+1; bh = max(ys)-min(ys)+1
        if bw <= 14 and bh <= 14 and 12 <= len(pix) <= 300 and len(pix) >= 0.35*bw*bh:
            dots.append(((min(xs)+max(xs))//2, (min(ys)+max(ys))//2, len(pix)))
    def inside_enclosed(cx, cy):
        for r in range(3, 9):
            hit = False
            for dy in range(-r, r+1):
                for dx in range(-r, r+1):
                    if max(abs(dx),abs(dy)) != r: continue
                    yy, xx = cy+dy, cx+dx
                    if 0 <= yy < h and 0 <= xx < w and not ink[yy*w+xx] and not seen[yy*w+xx]:
                        return True
                    if 0 <= yy < h and 0 <= xx < w and not ink[yy*w+xx]:
                        hit = True
            if hit: return False
        return False
    din = sum(1 for d in dots if inside_enclosed(d[0], d[1]))
    dout = len(dots) - din
    line = '%-10s paper=%3d ink=%5d enclosed=%5d dots=%d (in=%d out=%d) -> %s' % (
        name, paper, sum(ink), len(enclosed), len(dots), din, dout,
        'CLOSED+DOT' if (len(enclosed) >= min_enc and din >= 1) else
        ('CLOSED-no-dot' if len(enclosed) >= min_enc else 'OPEN'))
    print(line)
    return line

figs = [
 ('A1 blob',   95,225, 250,360),
 ('A2 circle',330,235, 450,360),
 ('A3 tri',   525,235, 695,390),
 ('A4 L',     775,250, 900,405),
 ('A5 flower',950,275,1080,400),
 ('B1 square',115,480, 250,640),
 ('B2 circle',325,490, 460,635),
 ('B3 squig', 515,500, 710,635),
 ('B4 V',     740,485, 910,640),
 ('B5 div',   955,545,1095,590),
 ('C1 fish',  140,710, 310,785),
 ('C2 para',  400,715, 575,800),
 ('C3 penta', 650,700, 750,785),
 ('C4 ticks', 925,700,1025,800),
 ('C5 cane',  175,845, 250,975),
 ('C6 blob',  435,850, 570,980),
 ('C7 star',  660,860, 790,970),
 ('C8 heart', 930,875,1030,965),
 ('C9 hash',  145,1080,265,1195),
 ('C10 bar',  400,1065,560,1205),
 ('C11 spiral',655,1060,810,1225),
 ('C12 rings',905,1075,1055,1245),
]
for f in figs:
    analyze(f[0], f[1], f[2], f[3], f[4])
