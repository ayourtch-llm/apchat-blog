import sys, math, collections
sys.path.insert(0,'scratch')
from img import load,lum
w,h,px=load()

def petal_count(x0,x1,y0,y1,th,nc=72,prom=3):
    pts=[]
    for y in range(y0,y1):
        for x in range(x0,x1):
            if lum(px(x,y))<th:
                pts.append((x,y))
    cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
    bins=collections.defaultdict(float)
    for x,y in pts:
        ang=math.degrees(math.atan2(y-cy,x-cx))
        r=math.hypot(x-cx,y-cy)
        b=int(((ang+180)%360)/360*nc)
        bins[b]=max(bins[b],r)
    rs=[bins.get(b,0.0) for b in range(nc)]
    sm=[(rs[(i-1)%nc]+rs[i]+rs[(i+1)%nc])/3 for i in range(nc)]
    mx=[]
    for i in range(nc):
        window=[sm[(i+k)%nc] for k in range(-6,7)]
        if sm[i]>=sm[(i-1)%nc] and sm[i]>sm[(i+1)%nc] and sm[i]-min(window)>prom:
            mx.append(i)
    merged=[]
    for i in mx:
        if merged and (i-merged[-1])%nc<=4:
            continue
        merged.append(i)
    return len(merged), merged, (round(cx,1),round(cy,1)), len(pts)

print("item5 flower:", petal_count(80,235,870,1015,62))
print("clover (B ex1):", petal_count(93,209,249,359,110))
