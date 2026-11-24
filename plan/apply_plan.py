# Writes the plan from plan_data.py into trip.html (safe to run again after editing the plan).
import json,re,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from plan_data import P
p='/home/nirtzur89/thailand/trip.html'
s=open(p,encoding='utf-8').read()
DOW=['ב׳','ג׳','ד׳','ה׳','ו׳','ש׳','א׳']
import datetime
def dm(d): y,m,dd=map(int,d.split('-'));return f'{dd}.{m}'
def dow(d): y,m,dd=map(int,d.split('-'));return DOW[datetime.date(y,m,dd).weekday()]
days=[];items=[]
for date,tab,stop,summ,its in P:
    days.append({'date':date,'tab':tab,'stop':stop})
    for i,it in enumerate(its):
        when,name,q,note,fl=it[:5]
        o={'id':f'{date[5:]}-{stop}-{i}','date':date,'tab':tab,'stop':stop,'when':when,'name':name,'q':q,'note':note}
        if 'o' in fl:o['opt']=1
        if 'b' in fl:o['book']=1
        if len(it)>5:o['rec']=it[5]
        items.append(o)
blk='<script type="application/json" id="trip-plan">'+json.dumps({'days':days,'items':items},ensure_ascii=False).replace('</','<\\/')+'</script>\n'
if 'id="trip-plan"' in s:
    s=re.sub(r'<script type="application/json" id="trip-plan">.*?</script>\n',lambda m:blk,s,flags=re.S)
else:
    k=s.index('<script type="application/json" id="trip-live">');s=s[:k]+blk+s[k:]

# Vietnam route list + day elements on the "next" page
vn_list='''  <ul class="stops2">
    <li><span>האנוי <span class="n">(מוזמן, 5.12–9.12)</span></span><span class="n">4 לילות</span></li>
    <li><span>סאפה <span class="n">(מוזמן, 9.12–13.12)</span></span><span class="n">4 לילות</span></li>
    <li><span>האנוי ושייט בהא לונג <span class="n">(מוזמן, 13.12–16.12)</span></span><span class="n">3 לילות</span></li>
    <li><span>✈ טיסה האנוי ← דה נאנג <span class="n">(מוזמן, 16.12, VJ511)</span></span><span class="n"></span></li>
    <li><span>הוי אן <span class="n">(16.12–21.12)</span></span><span class="n">5 לילות</span></li>
    <li><span>הואה <span class="n">(21.12–24.12)</span></span><span class="n">3 לילות</span></li>
    <li><span>הו צ׳י מין סיטי (סייגון) <span class="n">(24.12–27.12)</span></span><span class="n">3 לילות</span></li>
    <li><span>קאן תו, דלתת המקונג <span class="n">(27.12–28.12)</span></span><span class="n">לילה אחד</span></li>
    <li><span>סייגון, ליד שדה התעופה <span class="n">(28.12–29.12)</span></span><span class="n">לילה אחד</span></li>
    <li><span>✈ טיסה סייגון ← פוקט <span class="n">(29.12, יום לפני סוף הוויזה)</span></span><span class="n"></span></li>
  </ul>
'''
a=s.index('<h3 class="section-h">ויאטנם</h3>');b=s.index('<ul class="stops2">',a);e=s.index('</ul>',b)+6
s=s[:b].rstrip(' ')+vn_list.lstrip(' ') .join(['',''])+s[e:] if False else s[:b-2]+vn_list+s[e:]
vn=[d for d in P if d[1]=='next' and d[0]<'2026-12-29']
tl='<!--VN-DAYS-->\n  <h4 class="cat">🗓 ויאטנם, יום אחר יום (הצעה)</h4>\n  <p class="meta">המסלול הזה עוד לא הוזמן. הוא בנוי כך שבכל יום יש דבר מרכזי אחד בבוקר ומנוחה בצהריים. הימים בהוי אן, 16.12–21.12, נמצאים בלשונית ״הוי אן״.</p>\n  <div class="timeline">\n'+''.join(f'    <div class="day" data-date="{d[0]}"><h4>{dm(d[0])} <span class="dow">· יום {dow(d[0])}</span></h4><p>{d[3] or ""}</p></div>\n' for d in vn)+'  </div>\n<!--/VN-DAYS-->\n'
if '<!--VN-DAYS-->' in s:
    s=re.sub(r'<!--VN-DAYS-->.*?<!--/VN-DAYS-->\n',lambda m:tl,s,flags=re.S)
else:
    k=s.index('  <h3 class="section-h">דרום תאילנד</h3>');s=s[:k]+tl+'\n'+s[k:]

# day summaries on the stop pages
n=0
for date,tab,stop,summ,its in P:
    if not summ or (tab=='next' and date<'2026-12-29'): continue
    a=s.index('<div class="page" id="page-'+tab+'"');nx=s.find('<div class="page" id="page-',a+10);nx=len(s) if nx<0 else nx
    pat=re.compile(r'(<div class="day" data-date="'+date+r'"><h4>.*?</h4><p>)(.*?)(</p>)',re.S)
    seg,c=pat.subn(lambda m:m.group(1)+summ+m.group(3),s[a:nx],count=1)
    assert c==1,(date,tab);s=s[:a]+seg+s[nx:];n+=1
open(p,'w',encoding='utf-8').write(s)
print('days',len(days),'items',len(items),'summaries',n)
