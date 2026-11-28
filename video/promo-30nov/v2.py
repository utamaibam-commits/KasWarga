from eng import *
V=2; sc,TOTAL=timeline(V)
HEAD=(32,94,84);BGC=(236,229,221);ME=(214,246,196);INK=(22,28,30);MUT=(110,120,118);YEL=(255,205,40);RED=(220,50,60);GRN=(30,160,90)
def mkbg():
    im=Image.new('RGB',(W,H),BGC); d=ImageDraw.Draw(im); r=np.random.default_rng(4)
    for k in range(260):
        x,y=r.integers(0,W),r.integers(240,H); s=r.integers(8,22); c=(226,218,208)
        sh=r.integers(0,3)
        if sh==0: d.ellipse([x-s,y-s,x+s,y+s],outline=c,width=3)
        elif sh==1: d.rectangle([x-s,y-s,x+s,y+s],outline=c,width=3)
        else: d.line([x-s,y,x+s,y],fill=c,width=3);d.line([x,y-s,x,y+s],fill=c,width=3)
    d.rectangle([0,0,W,230],fill=HEAD)
    d.ellipse([120,95,210,185],fill=(200,220,214)); ttext(d,(165,140),'RT',F('inter',34,'Bold'),HEAD)
    d.text((240,92),'Grup Warga RT 05',font=F('inter',48,'Bold'),fill='white')
    d.text((240,152),'Bu Rina (Bendahara), Pak Joko, Bu Sri, +42',font=F('inter',30,'Regular'),fill=(200,225,218))
    d.text((60,108),'<',font=F('inter',60,'Bold'),fill='white')
    return im
BG=mkbg()
_bc={}
def bubble(text,me=False,name=None,ncol=(200,90,40),maxw=820,size=54,bad=False,good=False,doc=False):
    k=(text,me,name,bad,good,doc)
    if k in _bc: return _bc[k]
    f=F('inter',size,'Regular'); lines=[]
    for para in text.split('\n'): lines+=wrap(para,f,maxw) or ['']
    lh=int(size*1.32); w=max(f.getlength(l) for l in lines); w=max(w,220)
    top=54 if name else 0; extra=110 if doc else 0
    bw=int(w+60); bh=int(top+len(lines)*lh+70+extra)
    im=Image.new('RGBA',(bw+20,bh+20),(0,0,0,0)); d=ImageDraw.Draw(im)
    col=ME if me else (255,255,255)
    d.rounded_rectangle([10,10,10+bw,10+bh],30,fill=col+(255,))
    if bad: d.rounded_rectangle([10,10,10+bw,10+bh],30,outline=RED,width=6)
    if good: d.rounded_rectangle([10,10,10+bw,10+bh],30,outline=GRN,width=6)
    y=34
    if name: d.text((40,y),name,font=F('inter',34,'SemiBold'),fill=ncol); y+=top
    if doc:
        d.rounded_rectangle([34,y,bw-14,y+96],16,fill=(240,240,236)); d.rectangle([54,y+16,104,y+80],fill=RED); ttext(d,(79,y+48),'PDF',F('inter',22,'Bold'),'white')
        d.text((124,y+16),'Laporan-Kas-Nov.pdf',font=F('inter',36,'SemiBold'),fill=INK); d.text((124,y+58),'2 halaman',font=F('inter',26,'Regular'),fill=MUT); y+=extra
    for l in lines: d.text((40,y),l,font=f,fill=INK); y+=lh
    d.text((bw-120,10+bh-46),'19.0'+str(len(text)%10)+(' vv' if me else ''),font=F('inter',26,'Regular'),fill=MUT)
    _bc[k]=im; return im
def chat(cv,msgs,t,y0=280,ymax=1480):
    vis=[]
    for m in msgs:
        if t>=m[0]: vis.append(m)
    hs=[bubble(*m[1],**m[2]).height+14 for m in vis]; tot=sum(hs)
    off=max(0,tot-(ymax-y0))
    y=y0-off
    for m,h in zip(vis,hs):
        im=bubble(*m[1],**m[2]); me=m[1][1] if len(m[1])>1 else False
        p=t-m[0]; s=0.85+0.15*spring(p*1.5); a=eo(p/0.15)
        x=W-40-im.width if me else 40
        if y+h>y0-80: paste(cv,im,(x+im.width/2,y+im.height/2),scale=s,alpha=a)
        y+=h
def banner(cv,text,t0,t,y=1600,bg=YEL,fg=INK,size=64):
    p=t-t0
    if p<0: return
    while F('inter',size,'Black').getlength(text)>900: size-=2
    sp=tsprite(text,F('inter',size,'Black'),fg); im=Image.new('RGBA',(sp.width+80,sp.height+50),(0,0,0,0))
    ImageDraw.Draw(im).rounded_rectangle([0,0,im.width-1,im.height-1],28,fill=bg+(255,)); im.alpha_composite(sp,(40,25))
    paste(cv,im,(W/2,y),scale=0.5+0.5*spring(p*1.2),alpha=eo(p/0.15),angle=-2)
def tag(cv,text,t0,t):
    p=t-t0
    if p<0: return
    sp=tsprite(text,F('inter',44,'Black'),'white'); im=Image.new('RGBA',(sp.width+60,sp.height+30),(0,0,0,0))
    ImageDraw.Draw(im).rounded_rectangle([0,0,im.width-1,im.height-1],im.height//2,fill=HEAD+(255,)); im.alpha_composite(sp,(30,15))
    paste(cv,im,(W/2,300),scale=0.6+0.4*spring(p*1.3),alpha=eo(p/0.15))
IUR=phone('kaswarga-iuran',0,620,w=560)
def S(t0,text,me=False,**k): return (t0,(text,me),k)
def draw(t):
    s=scene_at(sc,t); i=s['i']; b=s['beats']; st=s['start']
    cv=BG.copy(); d=ImageDraw.Draw(cv)
    if i==0:
        chat(cv,[S(0.05,'Bu, iuran bulan ini berapa ya?',name='Pak Joko'),S(b[1]-0.2,'Saya kemarin udah bayar belum sih?',name='Bu Sri',ncol=(150,60,200)),
                 S(b[1]+0.6,'Kok saldo kas segitu doang?',name='Mas Andi',ncol=(30,110,200)),S(b[2]-0.4,'...',True)],t)
        banner(cv,'NAGIH IURAN = AWKWARD',b[1],t,1620,RED,(255,255,255),66)
    elif i==1:
        tag(cv,'TRIK #1 · TANGGAL TETAP',b[0],t)
        chat(cv,[S(b[0]+0.3,'Assalamualaikum warga. Iuran kas & sampah dibayar setiap TANGGAL 5 ya. Terima kasih.',True)],t,400)
        p=t-b[1]
        if p>0:
            cx,cy=W/2,1150; im=Image.new('RGBA',(420,420),(0,0,0,0)); dd=ImageDraw.Draw(im)
            dd.rounded_rectangle([10,10,410,410],40,fill='white'); dd.rounded_rectangle([10,10,410,110],40,fill=RED); dd.rectangle([10,70,410,110],fill=RED)
            ttext(dd,(210,62),'SETIAP BULAN',F('inter',40,'Black'),'white'); ttext(dd,(210,260),'5',F('inter',230,'Black'),INK)
            paste(cv,im,(cx,cy),scale=0.5+0.5*spring(p),angle=4)
            if t>b[2]: d.ellipse([cx-150,cy-90,cx+150,cy+200],outline=GRN,width=10)
        banner(cv,'Warga jadi hafal',b[-1],t,1620)
    elif i==2:
        tag(cv,'TRIK #2 · REKAP TERBUKA',b[0],t)
        chat(cv,[S(b[0]+0.3,'REKAP IURAN KAS NOVEMBER\nLunas 9 dari 16 rumah\nBlok A-1  lunas\nBlok A-2  lunas\nBlok A-3  lunas\nYang belum, ditunggu ya.',True),
                 S(b[2]-0.3,'Mantap Bu, jadi jelas!',name='Pak Joko'),S(b[2]+0.4,'Transparan, sip',name='Bu Sri',ncol=(150,60,200))],t,400)
        banner(cv,'Nggak ada yang ngerasa disindir',b[-1]+0.3,t,1620)
    elif i==3:
        tag(cv,'TRIK #3 · SANTAI & SOPAN',b[0],t)
        chat(cv,[S(b[0]+0.2,'PAK JOKO BELUM BAYAR!!! TOLONG SEGERA',True,bad=True),
                 S(b[1]+0.6,'Bapak/Ibu yang belum sempat, ditunggu sampai tanggal 10 ya. Terima kasih banyak',True,good=True)],t,400)
        if t>b[0]+0.6: 
            q=appear(t,b[0]+0.6); ttext(d,(110,560),'X',F('inter',int(120*q)+1,'Black'),RED)
        if t>b[1]+1.0:
            q=appear(t,b[1]+1.0); ttext(d,(110,860),'OK',F('inter',int(80*q)+1,'Black'),GRN)
        banner(cv,'Jangan sebut nama di grup',b[1]+1.4,t,1620)
    elif i==4:
        tag(cv,'BONUS · LAPORAN BULANAN',b[0],t)
        chat(cv,[S(b[0]+0.3,'Laporan kas RT bulan November, silakan dicek.',True,doc=True),
                 S(b[1]+0.1,'Makasih Bu Rina, jelas banget',name='Mas Andi',ncol=(30,110,200)),S(b[2],'Bendahara terbaik!',name='Bu Sri',ncol=(150,60,200))],t,400)
        banner(cv,'Warga percaya, bendahara aman',b[-1],t,1620,GRN,(255,255,255))
    else:
        d.rectangle([0,230,W,H],fill=(18,40,36))
        p=appear(t,b[0],0.5); paste(cv,IUR,(W/2,960+(1-p)*300),scale=1.08,alpha=p)
        ttext(d,(W/2,330),'Rekap & pengingat otomatis',F('inter',54,'Bold'),'white') if t>b[0] else None
        banner(cv,'KasWarga · Link di profil',b[0]+0.6,t,1600,YEL,INK,62)
        banner(cv,'Komen MAU buat lihat caranya',b[1],t,1760,(255,255,255),HEAD,50)
    return cv
def events():
    ev=[(0.05,'pop'),(sc[0]['beats'][1]-0.2,'pop'),(sc[0]['beats'][1]+0.6,'pop'),(sc[0]['beats'][1],'err')]
    for s in sc[1:]:
        b=s['beats']; ev+=[(s['start'],'swish'),(b[0],'pop'),(b[0]+0.3,'pop'),(b[-1],'ding' if s['i']<5 else 'thump')]
        if len(b)>2: ev.append((b[2],'pop'))
    ev.append((sc[-1]['beats'][1],'stamp')); return ev
main(V,draw,events,'chat',104,'v2-chat',sc,TOTAL)
