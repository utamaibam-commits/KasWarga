from eng import *
V=2; sc,TOTAL=timeline(V)
BLUE=(43,89,255);INK=(18,20,28);GRAY=(120,126,140)
def mkbg():
    y=np.linspace(0,1,H)[:,None];x=np.linspace(0,1,W)[None,:]
    r=250-6*y+0*x; g=250-4*y; b=252-1*y
    blob=np.exp(-(((x-0.85)**2)/0.08+((y-0.15)**2)/0.03))*1+np.exp(-(((x-0.1)**2)/0.06+((y-0.8)**2)/0.04))
    im=np.stack([r-14*blob,g-9*blob,b+0*blob],-1)
    return Image.fromarray(im.clip(0,255).astype(np.uint8))
BG=mkbg()
def word(cv,text,size,color,cx,cy,t0,t,w='ExtraBold',breathe=True,fromy=60):
    p=t-t0
    if p<0: return
    a=eo(p/0.35); sp=tsprite(text,F('inter',size,w),color)
    s=1+0.012*math.sin((t-t0)*2.4) if breathe else 1
    s*= lerp(0.92,1,eo(p/0.35))
    paste(cv,sp,(cx,cy+(1-a)*fromy),scale=s,alpha=a)
def chip(cv,text,cx,cy,t0,t,bg=BLUE,fg=(255,255,255),size=54):
    p=t-t0
    if p<0: return
    sp=tsprite(text,F('inter',size,'Bold'),fg); im=Image.new('RGBA',(sp.width+70,sp.height+36),(0,0,0,0))
    ImageDraw.Draw(im).rounded_rectangle([0,0,im.width-1,im.height-1],im.height//2,fill=bg+(255,)); im.alpha_composite(sp,(35,18))
    paste(cv,im,(cx,cy),scale=0.6+0.4*spring(p*1.3),alpha=eo(p/0.2))
IUR_LIST=card(shot('kaswarga-iuran',410,760),r=30,shadow_op=50,blur=34)
BELUM=card(shot('kaswarga-beranda',575,880),r=30,shadow_op=50,blur=34)
REKAP=card(shot('kaswarga-iuran',178,318),r=30,shadow_op=50,blur=34)
def cardin(cv,c,cx,cy,t0,t,scale=0.86):
    p=t-t0
    if p<0: return 0
    k=spring(p*1.1); drift=math.sin((t-t0)*1.3)*6
    paste(cv,c,(cx,cy+(1-eo(p/0.5))*220+drift),scale=scale*(0.94+0.06*k),alpha=eo(p/0.3)); return k
def ring(d,cx,cy,r,t0,t):
    p=t-t0
    if p<0: return
    for k in range(2):
        q=((p+k*0.45)%0.9)/0.9; rr=r*(1+q*0.6); a=int(255*(1-q))
        d.ellipse([cx-rr,cy-rr,cx+rr,cy+rr],outline=BLUE,width=6)
def draw(t):
    s=scene_at(sc,t); lt=t-s['start']; b=s['beats']; i=s['i']
    cv=BG.copy(); d=ImageDraw.Draw(cv)
    paste(cv,tsprite('@klisacom  ·  KasWarga',F('inter',34,'SemiBold'),GRAY),(W/2,150))
    pr=t/TOTAL; d.rounded_rectangle([140,195,940,201],3,fill=(225,228,236)); d.rounded_rectangle([140,195,140+800*pr,201],3,fill=BLUE)
    if i==0:
        word(cv,'Jadi',110,GRAY,W/2,520,b[0],t,'Bold')
        word(cv,'bendahara',175,INK,W/2,680,b[0]+0.25,t)
        word(cv,'RT?',260,BLUE,W/2,900,b[0]+0.6,t,'Black')
        word(cv,'pusing nagih',120,INK,W/2,1130,b[1],t)
        word(cv,'iuran tiap bulan?',100,GRAY,W/2,1270,b[1]+0.5,t,'Bold')
    elif i==1:
        word(cv,'tinggal',90,GRAY,W/2,300,b[0]+0.6,t,'Bold')
        word(cv,'centang.',150,BLUE,W/2,440,b[0]+1.0,t,'Black')
        cardin(cv,IUR_LIST,W/2,1010,b[0]+0.3,t,0.78)
        x0=W/2-IUR_LIST.width*0.82/2
        if t>b[0]+1.4:
            for k,yy in enumerate([660,820,980]): 
                pass
        chip(cv,'✓ lunas',380,1500,b[0]+2.6,t,bg=(22,163,74))
        chip(cv,'belum',700,1500,b[0]+3.0,t,bg=(225,29,72))
    elif i==2:
        word(cv,'yang belum bayar?',110,INK,W/2,400,b[0],t)
        cardin(cv,BELUM,W/2,850,b[0]+0.35,t,0.82)
        chip(cv,'kirim pengingat via WhatsApp',W/2,1380,b[0]+1.9,t,bg=(22,163,74),size=50)
    elif i==3:
        word(cv,'rekap iuran',130,INK,W/2,380,b[0],t)
        word(cv,'sekali klik.',150,BLUE,W/2,540,b[0]+0.45,t,'Black')
        k=cardin(cv,REKAP,W/2,900,b[0]+0.3,t,0.88)
        sc_=0.88; cw,chh=REKAP.width*sc_,REKAP.height*sc_
        bx=W/2-cw/2+(68+80*3)*sc_; by=900-chh/2+(68+78*3)*sc_
        if t>b[0]+1.1: ring(d,bx,by,110,b[0]+1.1,t)
        chip(cv,'→ grup WA warga',W/2,1300,b[0]+1.8,t,size=56)
    elif i==4:
        word(cv,'data di HP kamu.',120,INK,W/2,480,b[0],t)
        word(cv,'tanpa akun.',125,BLUE,W/2,680,b[0]+1.0,t,'Black')
        word(cv,'tanpa internet.',125,BLUE,W/2,860,b[0]+1.9,t,'Black')
        if len(b)>1:
            word(cv,'anjay,',100,GRAY,W/2,1100,b[1],t,'Bold')
            word(cv,'transparan banget!',110,INK,W/2,1240,b[1]+0.4,t)
    else:
        word(cv,'KasWarga',175,INK,W/2,520,b[0],t,'Black')
        word(cv,'kas RT · iuran · arisan',64,GRAY,W/2,690,b[0]+0.4,t,'SemiBold')
        word(cv,'Rp39.000',170,BLUE,W/2,880,b[0]+0.7,t,'Black')
        word(cv,'cek link di bio',96,INK,W/2,1100,b[1],t)
        chip(cv,'lynk.id/ibam2178',W/2,1250,b[1]+0.4,t,size=64)
    if i in (1,2,3):
        paste(cv,tsprite('*data contoh',F('inter',30,'Medium'),GRAY),(930,1580))
    # scene transition: white flash slide
    if i>0 and lt<0.25:
        a=1-lt/0.25; ov=Image.new('RGB',(W,H),(255,255,255)); cv=Image.blend(cv,ov,a*0.85)
    return cv
def events():
    ev=[]
    for s in sc:
        b=s['beats']
        if s['i']>0: ev.append((s['start'],'swish'))
        for x in b: ev.append((x,'pop'))
    S=sc
    ev+=[(S[0]['beats'][0]+0.6,'thump'),(S[1]['beats'][0]+0.3,'whoosh'),(S[1]['beats'][0]+1.0,'thump'),(S[1]['beats'][0]+2.6,'ding'),(S[1]['beats'][0]+3.0,'err'),
         (S[2]['beats'][0]+0.35,'whoosh'),(S[2]['beats'][0]+1.9,'ding'),(S[3]['beats'][0]+0.45,'thump'),(S[3]['beats'][0]+1.1,'click'),(S[3]['beats'][0]+1.8,'pop'),
         (S[4]['beats'][0]+1.0,'thump'),(S[4]['beats'][0]+1.9,'thump'),(S[5]['beats'][0],'thump'),(S[5]['beats'][0]+0.7,'ding'),(S[5]['beats'][-1]+0.4,'pop')]
    return ev
if __name__=='__main__': main(V,draw,events,'clean',104,'v2-kaswarga-hurufbernapas',sc,TOTAL)
