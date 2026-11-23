# Builds the day-by-day data the email routines read (encrypted before publishing).
import re,json,sys,html,datetime
s=open(sys.argv[1],encoding='utf-8').read()
live=json.loads(re.search(r'id="trip-live">(.*?)</script>',s,re.S).group(1))
plan=json.loads(re.search(r'id="trip-plan">(.*?)</script>',s,re.S).group(1))
stops=json.loads(re.search(r"var STOPS=(\[\[.*?\]\]);",s).group(1).replace("'",'"'))
strip=lambda x:re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',x))).strip()
stays=[]
for m in re.finditer(r'<article class="card stay">(.*?)</article>',s,re.S):
    t=re.search(r'class="type">(.*?)</span>',m.group(1));h=re.search(r'<h3[^>]*>(.*?)</h3>',m.group(1))
    d=t and re.search(r'(\d{1,2})\.(\d{1,2})\s*[–-]\s*(\d{1,2})\.(\d{1,2})',t.group(1))
    if not(d and h):continue
    iso=lambda dd,mm:('2026' if int(mm)>=11 else '2027')+'-%02d-%02d'%(int(mm),int(dd))
    stays.append((iso(d.group(1),d.group(2)),iso(d.group(3),d.group(4)),strip(h.group(1))))
texts={}
for m in re.finditer(r'<div class="day" data-date="([^"]+)"><h4>.*?</h4><p>(.*?)</p>',s,re.S):
    t=strip(m.group(2))
    if t and t not in texts.setdefault(m.group(1),[]):texts[m.group(1)].append(t)
DOW=['ב׳','ג׳','ד׳','ה׳','ו׳','ש׳','א׳']
days={}
d=datetime.date(2026,11,23)
while d<=datetime.date(2027,1,21):
    k=d.isoformat();place=''
    for a,b in stops:
        if a<=k:place=b
    ev=[]
    for e in live.get('events',[]):
        at=e['at']
        if at[:10]==k: ev.append({'time':'' if e.get('day') else at[11:16],'t':e['t'],'n':e.get('n',''),'major':bool(e.get('major'))})
    days[k]={'dow':DOW[d.weekday()],'trip_day':(d-datetime.date(2026,11,22)).days+1,'place':place,
      'hotel':next((h for a,b,h in stays if a<=k<b),''),'summary':texts.get(k,[]),'events':sorted(ev,key=lambda x:x['time']),
      'plan':[{x:i[x] for x in('when','name','note','opt','book') if x in i} for i in plan['items'] if i['date']==k]}
    d+=datetime.timedelta(days=1)
json.dump({'notice':live.get('notice',''),'site':sys.argv[2],'days':days},sys.stdout,ensure_ascii=False)
