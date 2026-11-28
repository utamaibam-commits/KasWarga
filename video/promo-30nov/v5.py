from eng import *
V=5; sc,TOTAL=timeline(V)
YEL=(255,222,0);MAG=(236,0,140);CYA=(0,174,239);INK=(15,15,15);WH=(255,255,255);RED=(237,28,36)
def halftone(col,dot,seed=0,size=(W,H)):
    im=Image.new('RGB',size,col); d=ImageDraw.Draw(im); step=34
    c2=tuple(int(c*0.82) for c in col)
    for yy in range(0,size[1]+step,step):
        for xx in range(0,size[0]+step,step):
            off=step/2 if (yy//step)%2 else 0; r=dot*(0.5+0.5*math.sin((xx+yy)/260+seed))
            d.ellipse([xx+off-r,yy-r,xx+off+r,yy+r],fill=c2)
    return im
BGS=[halftone(YEL,9,0),halftone(CYA,9,1),halftone(MAG,9,2),halftone(YEL,9,3),halftone(CYA,9,4),halftone(MAG,9,5)]
def burst(text,col,fg=INK,size=150,n=14,r1=330,r2=240,ang=0):
    f=F('bang',size); tw=f.getlength(text); r1=max(r1,tw/2+110); r2=max(r2,tw/2+40)
    S=int(r1*2+40); im=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(im); c=S/2
    pts=[(c+(r1 if k%2==0 else r2)*math.cos(math.pi*k/n+ang),c+(r1 if k%2==0 else r2)*0.62*math.sin(math.pi*k/n+ang)) for k in range(2*n)]
    d.polygon([(x+12,y+14) for x,y in pts],fill=INK); d.polygon(pts,fill=col,outline=INK); d.line(pts+[pts[0]],fill=INK,width=10)
    d.text((c,c),text,font=f,fill=fg,anchor='mm',stroke_width=6,stroke_fill=INK if fg!=INK else WH)
    return im
def caption(cv,text,t0,t,y=230):
    p=t-t0
    if p<0: return
    f=F('bang',68); lines=wrap(text,f,860); h=len(lines)*78+50; w=int(max(f.getlength(l) for l in lines))+70
    im=Image.new('RGBA',(w+16,h+16),(0,0,0,0)); d=ImageDraw.Draw(im); d.rectangle([12,12,w+12,h+12],fill=INK); d.rectangle([0,0,w,h],fill=(255,248,200),outline=INK,width=7)
    for k,l in enumerate(lines): d.text((35,25+k*78),l,font=f,fill=INK)
    paste(cv,im,(W/2,y+h/2),scale=0.8+0.2*eo(p/0.2),alpha=eo(p/0.12))
def panel(name,y0,y1,w=760,ang=0):
    sh=fit(shot(name,y0,y1),w=w); im=Image.new('RGBA',(sh.width+40,sh.height+40),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([22,22,sh.width+36,sh.height+36],fill=INK); im.paste(sh,(8,8)); d.rectangle([4,4,sh.width+12,sh.height+12],outline=INK,width=10)
    return im
P_IUR=panel('kaswarga-iuran',380,820); P_REK=panel('kaswarga-iuran',110,350); P_ARI=panel('kaswarga-arisan',0,560,700); P_LAP=panel('kaswarga-laporan',60,560,700); P_HOME=panel('kaswarga-beranda',0,480,640)
def pin(cv,im,t0,t,cy=1050,ang=-2,fromx=0):
    p=t-t0
    if p<0: return
    paste(cv,im,(W/2+(1-eo(p/0.35))*fromx,cy+(1-eo(p/0.35))*(0 if fromx else 500)),angle=ang,scale=0.9+0.1*spring(p*1.2))
def pow_(cv,text,col,cx,cy,t0,t,size=150,fg=INK,ang=-0.2):
    p=t-t0
    if p<0: return
    bi=burst(text,col,fg,size); k=min(1,1000/bi.width); paste(cv,bi,(cx,cy),scale=k*lerp(0.2,1,spring(p*1.4)),angle=-8+4*math.sin(p*3))
def draw(t):
    s=scene_at(sc,t); i=s['i']; b=s['beats']; lt=t-s['start']
    cv=BGS[i].copy(); d=ImageDraw.Draw(cv)
    d.rectangle([0,H-120,W,H],fill=INK); ttext(d,(W/2,H-60),'@klisacom  ·  KasWarga',F('bang',46),YEL)
    if i==0:
        pow_(cv,'BENDAHARA RT!',WH,W/2,620,0.03,t,150)
        pow_(cv,'5 MENIT',RED,W/2,1150,b[1]-0.1,t,190,WH)
        if t>b[1]+0.5: caption(cv,'...dan kerjaanmu KELAR!',b[1]+0.5,t,1500)
    elif i==1:
        caption(cv,'Iuran tinggal centang. Lunas & belum langsung kelihatan!',b[0],t)
        pin(cv,P_IUR,b[0]+0.15,t,1040,-2)
        pow_(cv,'CENTANG!',YEL,760,1560,b[1],t,120)
    elif i==2:
        caption(cv,'Rekap iuran ke grup WhatsApp, sekali klik!',b[0],t)
        pin(cv,P_REK,b[0]+0.15,t,900,2,900)
        pow_(cv,'KLIK!',YEL,330,1420,b[1]-0.4,t,170)
    elif i==3:
        caption(cv,'Arisan? Catat setoran & kocok pemenang di HP!',b[0],t)
        pin(cv,P_ARI,b[0]+0.15,t,1080,-3)
        pow_(cv,'KOCOK!',RED,780,1600,b[1],t,150,WH)
    elif i==4:
        caption(cv,'Buku kas RT + laporan siap cetak. Tanpa akun!',b[0],t)
        pin(cv,P_LAP,b[0]+0.15,t,1080,2,-900)
        pow_(cv,'CETAK!',YEL,300,1600,b[1],t,150)
    else:
        pin(cv,P_HOME,b[0],t,820,-2)
        pow_(cv,'Rp39RB',RED,W/2,1360,b[0]+0.3,t,190,WH)
        if t>b[0]+1.0: caption(cv,'Sekali bayar · Link di profil · Komen MAU!',b[0]+1.0,t,1560)
    if lt<0.12 and i>0:
        a=int(255*(1-lt/0.12)); ov=Image.new('RGB',(W,H),WH); cv=Image.blend(cv,ov,a/255*0.8)
    return cv
def events():
    ev=[(0.03,'stamp'),(sc[0]['beats'][1]-0.1,'stamp')]
    for s in sc[1:]:
        b=s['beats']; ev+=[(s['start'],'whoosh'),(b[0]+0.15,'thump')]
        if len(b)>1: ev.append((b[1] if s['i'] not in (2,) else b[1]-0.4,'stamp'))
    ev+=[(sc[5]['beats'][0]+0.3,'stamp'),(sc[5]['beats'][-1],'ding')]; return ev
main(V,draw,events,'pop',118,'v5-komik',sc,TOTAL)
