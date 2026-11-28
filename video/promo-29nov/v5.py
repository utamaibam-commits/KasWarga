from eng import *
V=5; sc,TOTAL=timeline(V)
CRM=(246,233,215);TER=(217,101,59);MUS=(232,176,74);OLV=(110,139,78);PLM=(61,44,62);PCH=(242,181,160);SKY=(250,222,190)
rng=np.random.default_rng(11)
GR=(rng.standard_normal((H,W,1))*9).astype(np.float32)
def grain(im):
    a=np.asarray(im).astype(np.float32)+GR; return Image.fromarray(a.clip(0,255).astype(np.uint8))
def mkbg():
    im=Image.new('RGB',(W,H),CRM); d=ImageDraw.Draw(im)
    d.ellipse([760,1180,1060,1480],fill=PCH)  # sun
    # hills
    d.ellipse([-300,1420,800,2100],fill=(226,200,160)); d.ellipse([400,1460,1500,2150],fill=(214,186,146))
    # houses
    xs=[60,250,440,640,840]
    cols=[TER,MUS,OLV,PCH,TER]
    for k,x in enumerate(xs):
        y=1560+(k%2)*30; w_=170
        d.rectangle([x,y,x+w_,y+170],fill=cols[k]); d.polygon([(x-15,y),(x+w_/2,y-95),(x+w_+15,y)],fill=PLM)
        d.rectangle([x+60,y+80,x+110,y+170],fill=PLM); d.rectangle([x+20,y+30,x+50,y+60],fill=CRM); d.rectangle([x+120,y+30,x+150,y+60],fill=CRM)
    return im
BG=mkbg()
def txt(cv,s,size,col,cx,cy,t0,t,w='Bold'):
    if t<t0: return
    p=t-t0; sp=tsprite(s,F('fred',size,w),col)
    paste(cv,sp,(cx,cy+(1-eo(p/0.3))*40),scale=0.7+0.3*spring(p*1.2),alpha=eo(p/0.2))
def flatcard(im,sc_):
    im=im.resize((int(im.width*sc_),int(im.height*sc_)),Image.LANCZOS); im=rounded(im,26)
    o=Image.new('RGBA',(im.width+24,im.height+24),(0,0,0,0)); ImageDraw.Draw(o).rounded_rectangle([18,18,o.width-1,o.height-1],30,fill=PLM+(255,))
    ImageDraw.Draw(o).rounded_rectangle([0,0,im.width+5,im.height+5],30,fill=PLM+(255,))
    o.alpha_composite(im,(3,3)); return o
HERO=flatcard(shot('kaswarga-arisan',62,306),0.74)
SETOR=flatcard(shot('kaswarga-arisan',628,765),0.66)
KOCOK=flatcard(shot('kaswarga-arisan',318,606),0.74)
RIW=flatcard(shot('kaswarga-arisan',628,1000),0.62)
KAS=flatcard(shot('kaswarga-kas',60,372),0.55)
LAP=flatcard(shot('kaswarga-laporan',172,500),0.55)
def cardin(cv,c,cx,cy,t0,t,ang=0):
    if t<t0: return
    p=t-t0; paste(cv,c,(cx,cy+(1-eo(p/0.4))*160+math.sin(p*1.6)*5),scale=0.85+0.15*spring(p*1.1),angle=ang,alpha=eo(p/0.25))
def jar(cv,cx,cy,s,t,shake=0):
    im=Image.new('RGBA',(400,480),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([40,90,360,470],60,fill=(214,232,226,255)); d.rectangle([90,40,310,100],fill=TER+(255,))
    r=np.random.default_rng(4)
    for k in range(14):
        x=int(r.integers(80,300)); y=int(r.integers(260,430)); a=r.integers(0,180)
        c=[MUS,PCH,CRM,OLV][k%4]; sl=Image.new('RGBA',(80,34),c+(255,)); ImageDraw.Draw(sl).line([(10,17),(70,17)],fill=PLM+(255,),width=3)
        sl=sl.rotate(a+shake*30*math.sin(t*20+k),expand=True); im.alpha_composite(sl,(x-sl.width//2,y-sl.height//2))
    d.rounded_rectangle([70,130,110,330],20,fill=(255,255,255,120))
    ang=shake*12*math.sin(t*28)
    paste(cv,im,(cx,cy),scale=s,angle=ang)
def draw(t):
    s=scene_at(sc,t); lt=t-s['start']; b=s['beats']; i=s['i']
    cv=BG.copy(); d=ImageDraw.Draw(cv)
    paste(cv,tsprite('@klisacom · KasWarga',F('fred',38,'SemiBold'),PLM),(W/2,150))
    if i==0:
        txt(cv,'arisan ibu-ibu RT',80,PLM,W/2,380,b[0],t,'SemiBold')
        txt(cv,'masih pakai',80,PLM,W/2,480,b[0]+0.5,t,'SemiBold')
        txt(cv,'kertas digulung?',120,TER,W/2,620,b[0]+1.0,t)
        sh=1 if b[0]+2.4<t<b[0]+3.6 else 0.15
        jar(cv,W/2,1050,1.0,t,sh)
        if t>b[0]+2.6:
            p=t-b[0]-2.6; im=Image.new('RGBA',(520,170),(0,0,0,0)); ImageDraw.Draw(im).rounded_rectangle([0,0,519,169],85,fill=MUS+(255,))
            im.alpha_composite(tsprite('anjir, jadul!',F('fred',84,'Bold'),PLM),(50,30)); paste(cv,im,(W/2+160,1330),scale=0.6+0.4*spring(p*1.3),angle=-6)
    elif i==1:
        txt(cv,'KasWarga punya',80,PLM,W/2,330,b[0],t,'SemiBold')
        txt(cv,'fitur ARISAN',130,TER,W/2,460,b[0]+0.4,t)
        cardin(cv,HERO,W/2,840,b[0]+0.5,t,-2)
        if len(b)>1:
            cardin(cv,SETOR,W/2,1265,b[1],t,2)
            txt(cv,'catat setoran tiap putaran',58,OLV,W/2,1455,b[1]+0.5,t,'SemiBold')
    elif i==2:
        txt(cv,'kocok pemenang',100,PLM,W/2,330,b[0],t)
        txt(cv,'acak, langsung di HP',80,TER,W/2,450,b[0]+0.5,t,'SemiBold')
        cardin(cv,KOCOK,W/2,850,b[0]+0.4,t)
        jar(cv,880,1200,0.42,t,1 if t>b[0]+1.0 else 0.2)
        if len(b)>1:
            txt(cv,'yang udah menang,',70,PLM,W/2,1310,b[1],t,'SemiBold')
            txt(cv,'nggak ikut lagi',90,OLV,W/2,1410,b[1]+0.4,t)
    elif i==3:
        txt(cv,'riwayat pemenang',96,PLM,W/2,320,b[0],t)
        txt(cv,'tersimpan',120,TER,W/2,440,b[0]+0.4,t)
        cardin(cv,RIW,W/2,930,b[0]+0.3,t,-1.5)
        if t>b[0]+1.8:
            p=t-b[0]-1.8; im=Image.new('RGBA',(400,400),(0,0,0,0)); ImageDraw.Draw(im).ellipse([0,0,399,399],fill=MUS+(255,))
            im.alpha_composite(tsprite('no',F('fred',100,'Bold'),PLM),(140,90)); im.alpha_composite(tsprite('drama!',F('fred',96,'Bold'),PLM),(58,190))
            paste(cv,im,(860,1330),scale=(0.6+0.4*spring(p*1.3))*0.7,angle=12)
    elif i==4:
        txt(cv,'plus buku kas RT',96,PLM,W/2,330,b[0],t)
        txt(cv,'& laporan siap cetak',80,TER,W/2,450,b[0]+0.8,t,'SemiBold')
        cardin(cv,KAS,330,900,b[0]+0.3,t,-4)
        cardin(cv,LAP,760,1050,b[0]+1.0,t,4)
    else:
        txt(cv,'KasWarga',190,TER,W/2,460,b[0],t)
        txt(cv,'kas RT · iuran · arisan',62,PLM,W/2,620,b[0]+0.4,t,'SemiBold')
        if t>b[0]+0.8:
            p=t-b[0]-0.8; im=Image.new('RGBA',(560,200),(0,0,0,0)); ImageDraw.Draw(im).rounded_rectangle([0,0,559,199],100,fill=OLV+(255,))
            sp=tsprite('Rp39.000',F('fred',110,'Bold'),CRM); im.alpha_composite(sp,(280-sp.width//2,100-sp.height//2)); paste(cv,im,(W/2,820),scale=0.6+0.4*spring(p*1.3))
        txt(cv,'link ada di bio!',100,PLM,W/2,1040,b[-1],t)
        txt(cv,'lynk.id/ibam2178',70,TER,W/2,1160,b[-1]+0.4,t,'SemiBold')
    if i in (1,2,3,4): paste(cv,tsprite('*data contoh',F('fred',34,'Medium'),PLM),(W/2,200))
    if i>0 and lt<0.3:
        r=eo(lt/0.3)*1400; a=1-lt/0.3; ov=Image.new('L',(W,H),0); ImageDraw.Draw(ov).ellipse([W/2-r,H/2-r,W/2+r,H/2+r],fill=int(255*a))
        cv=Image.composite(Image.new('RGB',(W,H),MUS),cv,ov)
    return grain(cv)
def events():
    ev=[];S=sc
    for s in S:
        if s['i']>0: ev.append((s['start'],'swish'))
        for x in s['beats']: ev.append((x,'pop'))
    b=S[0]['beats']; ev+=[(b[0]+1.0,'pop'),(b[0]+2.4,'shake'),(b[0]+2.6,'thump')]
    b=S[1]['beats']; ev+=[(b[0]+0.5,'whoosh'),(b[-1],'whoosh')]
    b=S[2]['beats']; ev+=[(b[0]+0.4,'whoosh'),(b[0]+1.0,'shake'),(b[0]+1.7,'shake'),(b[-1]+0.4,'ding')]
    b=S[3]['beats']; ev+=[(b[0]+0.3,'whoosh'),(b[0]+1.8,'thump')]
    b=S[4]['beats']; ev+=[(b[0]+0.3,'whoosh'),(b[0]+1.0,'whoosh')]
    b=S[5]['beats']; ev+=[(b[0]+0.8,'ding'),(b[-1],'thump')]
    return ev
if __name__=='__main__': main(V,draw,events,'warm',92,'v5-kaswarga-datarberbutir',sc,TOTAL)
