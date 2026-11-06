from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np, math
S=4; N=120*S; C=N/2
def disc(r, cx=C, cy=C):
    m=Image.new('L',(N,N),0); ImageDraw.Draw(m).ellipse((cx-r,cy-r,cx+r,cy+r),fill=255); return m
def grad_layer(R, col_in, col_out, a_in, a_out, off=(0,0)):
    y,x=np.mgrid[0:N,0:N].astype(float)
    d=np.hypot(x-(C+off[0]*S),y-(C+off[1]*S))/R
    d=np.clip(d,0,1.4)
    t=np.clip(d,0,1)[...,None]
    rgb=np.array(col_in)*(1-t)+np.array(col_out)*t
    a=a_in*(1-t[...,0])+a_out*t[...,0]
    return np.dstack([rgb,a*255])
def blur(im,r): return im.filter(ImageFilter.GaussianBlur(r*S))
def bubble(locked, lockmask=None):
    R=46*S
    y,x=np.mgrid[0:N,0:N].astype(float)
    m=np.array(disc(R)).astype(float)/255
    d=np.clip(np.hypot(x-C,y-C)/R,0,1)
    # dew body: nearly clear, a touch denser toward the edge
    if locked:
        col=np.array([150,205,215]); base=0.30; edge=0.30
    else:
        col=np.array([215,242,248]); base=0.07; edge=0.22
    a=(base+edge*d**3)*m
    rgb=np.dstack([np.full((N,N),c) for c in col])
    # refracted light pooled bottom-right inside the drop
    cau=np.exp(-(((x-(C+14*S))**2+(y-(C+20*S))**2)/(2*(17*S)**2)))
    ring=np.clip((d-0.55)/0.45,0,1)
    cmask=cau*ring
    rgb=rgb*(1-0.7*cmask[...,None])+np.array([255,255,255])*0.7*cmask[...,None]
    a=np.clip(a+0.38*cmask*m,0,1)
    body=Image.fromarray(np.dstack([rgb,a*255]).astype('uint8'),'RGBA')
    out=Image.new('RGBA',(N,N),(0,0,0,0))
    # soft contact shadow under the drop
    sh=Image.new('RGBA',(N,N),(0,0,0,0))
    sm_=disc(R-2*S,C+3*S,C+6*S)
    sh.putalpha(sm_.point(lambda v:int(v*0.34)))
    sh=Image.alpha_composite(Image.new('RGBA',(N,N),(20,70,85,0)),Image.merge('RGBA',(Image.new('L',(N,N),20),Image.new('L',(N,N),70),Image.new('L',(N,N),85),sh.getchannel('A'))))
    out=Image.alpha_composite(out,blur(sh,3.5))
    # carve the drop body out of its own shadow so the centre stays see-through
    hole=np.array(disc(R)).astype(float)/255
    oa=np.array(out).astype(float); oa[...,3]*=(1-hole*0.85); out=Image.fromarray(oa.astype('uint8'),'RGBA')
    out=Image.alpha_composite(out,body)
    # frosted grain + faint water ripples inside the body
    rng=np.random.default_rng(7 if locked else 3)
    g=Image.fromarray((rng.random((N//2,N//2))*255).astype('uint8')).resize((N,N),Image.BICUBIC).filter(ImageFilter.GaussianBlur(0.8*S))
    g=np.array(g).astype(float); g=(g-g.mean())/(g.std()+1e-6)
    rip=np.sin((x*0.9+y*0.5)/ (3.2*S) + 2.2*np.sin(y/(9*S)))*0.5+0.5
    inner=np.array(disc(R-3*S)).astype(float)/255
    tl=np.clip(g*0.5+0.5,0,1)
    wa=np.clip((0.10*np.clip(g,0,3)/3+0.07*rip*(1-d)**0.5)*inner,0,1)
    da=np.clip(0.07*np.clip(-g,0,3)/3*inner,0,1)
    wl=Image.fromarray(np.dstack([np.full((N,N),255),np.full((N,N),255),np.full((N,N),255),wa*255]).astype('uint8'),'RGBA')
    dk=Image.fromarray(np.dstack([np.full((N,N),40),np.full((N,N),90),np.full((N,N),110),da*255]).astype('uint8'),'RGBA')
    out=Image.alpha_composite(out,dk); out=Image.alpha_composite(out,wl)
    # thin darker meniscus at upper-left inside edge (refraction), crisp bright rim lower-right
    ly=Image.new('RGBA',(N,N),(0,0,0,0)); dl=ImageDraw.Draw(ly)
    import colorsys
    for k in range(0,360,3):
        t=k/360.0
        # blue (upper-left) to pink (lower-right) sweep
        u=0.5+0.5*np.cos(np.radians(k-45))
        col=(int(110+120*u),int(170-50*u),int(240-20*u))
        al=int(95+110*u)
        dl.arc((C-R+1*S,C-R+1*S,C+R-1*S,C+R-1*S),start=k,end=k+4,fill=col+(al,),width=int(2.4*S))
    out=Image.alpha_composite(out,blur(ly,0.5))
    # sharp top-left window highlight
    hl=Image.new('RGBA',(N,N),(0,0,0,0)); dh=ImageDraw.Draw(hl)
    r2=R-6*S
    dh.arc((C-r2,C-r2,C+r2,C+r2),start=200,end=255,fill=(255,255,255,235),width=int(3.0*S))
    out=Image.alpha_composite(out,blur(hl,0.7))
    sp=Image.new('RGBA',(N,N),(0,0,0,0))
    ImageDraw.Draw(sp).ellipse((C-26*S,C-31*S,C-10*S,C-21*S),fill=(255,255,255,235))
    sp=sp.rotate(32,center=(C-18*S,C-26*S))
    out=Image.alpha_composite(out,blur(sp,1.2))
    dd=Image.new('RGBA',(N,N),(0,0,0,0)); ImageDraw.Draw(dd).ellipse((C+19*S,C+24*S,C+24*S,C+29*S),fill=(255,255,255,230))
    out=Image.alpha_composite(out,blur(dd,0.6))
    if lockmask is not None:
        lk=Image.new('RGBA',(N,N),(255,255,255,0)); lk.putalpha(lockmask.point(lambda v:int(v*0.92)))
        out=Image.alpha_composite(out,lk)
    return out.resize((120,120),Image.LANCZOS)
sheet=Image.open('images/shared-0-sheet14.orig.webp').convert('RGBA')
# lock glyph: bright pixels in locked original frame
orig=sheet.crop((897,897,1017,1017))
a=np.array(orig).astype(float)
bright=(a[...,0]>200)&(a[...,1]>200)&(a[...,3]>200)
lm0=Image.fromarray((bright*255).astype('uint8'),'L').resize((N,N),Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2*S))
k=0.74; sm=lm0.resize((int(N*k),int(N*k)),Image.LANCZOS)
lm=Image.new('L',(N,N),0); lm.paste(sm,(int((N-sm.width)/2),int((N-sm.height)/2)+2*S))
lm=lm.point(lambda v:255 if v>150 else (0 if v<90 else int((v-90)*255/60)))
out=sheet.copy()
for (x,y),img in [((897,1537),bubble(False)),((897,897),bubble(True,lm))]:
    box=(x,y,x+120,y+120)
    blank=Image.new('RGBA',(120,120),(0,0,0,0))
    out.paste(blank,box); out.alpha_composite(img,(x,y))
out.save('images/shared-0-sheet14.webp',lossless=True,quality=100,method=6)
# preview
bg=Image.new('RGBA',(560,260),(250,140,110,255))
for i,(x,y) in enumerate([(897,1537),(897,897)]):
    c=out.crop((x,y,x+120,y+120)).resize((240,240)); bg.paste(c,(10+i*280,10),c)
bg.save('/tmp/claude/new_frames.png')
