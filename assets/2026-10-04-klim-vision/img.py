import struct

def load(path='scratch/page.bmp'):
    f=open(path,'rb').read()
    off=struct.unpack_from('<I',f,10)[0]
    w=struct.unpack_from('<i',f,18)[0]
    h=abs(struct.unpack_from('<i',f,22)[0])
    bpp=struct.unpack_from('<H',f,28)[0]
    assert bpp==24, bpp
    rowbytes=w*3
    data=f[off:off+rowbytes*h]
    # top-down (h was negative)
    def px(x,y):
        if x<0 or y<0 or x>=w or y>=h: return 255,255,255
        i=y*rowbytes+x*3
        return data[i],data[i+1],data[i+2]
    return w,h,px

def lum(px):
    r,g,b=px
    return (r*299+g*587+b*114)//1000

def render(w,h,px,x0,y0,x1,y1,tw=140,thresh=140):
    # sample grid tw wide; height scaled by aspect
    x1=min(x1,w); y1=min(y1,h)
    cw=x1-x0; ch=y1-y0
    th=max(1,int(round(tw*ch/cw)))
    out=[]
    for j in range(th):
        yy=y0+int(j*ch/th)
        row=[]
        for i in range(tw):
            xx=x0+int(i*cw/tw)
            # 2x2 block min-lum for better line capture
            l=min(lum(px(xx+dx,yy+dy)) for dx in (0,1) for dy in (0,1))
            row.append('#' if l<thresh else ' ')
        out.append(''.join(row))
    return '\n'.join(out)

if __name__=='__main__':
    w,h,px=load()
    print("dims",w,h)
    print(render(w,h,px,0,0,w,h,tw=150))
