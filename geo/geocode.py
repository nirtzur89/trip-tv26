# Looks up coordinates for each recommended place (OpenStreetMap Nominatim, 1 request/second). Output: geo.json
import re,json,time,urllib.parse as U,urllib.request as R,math,html,os,sys
src,out=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
C={'bangkok':(13.75,100.50),'chiangmai':(18.79,98.98),'pai':(19.36,98.44),'chiangrai':(19.91,99.83),'hanoi':(21.03,105.85),'sapa':(22.34,103.84),'hoian':(15.88,108.33)}
NEXT=[(8.69,98.25),(8.05,98.76),(13.75,100.50),(20.25,105.97),(8.45,98.52),(8.9,98.8),(8.88,98.35)]
def km(a,b):
    la1,lo1,la2,lo2=map(math.radians,(a[0],a[1],b[0],b[1]));h=math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 12742*math.asin(math.sqrt(h))
geo=json.load(open(out)) if os.path.exists(out) else {}
pages=re.split(r'<div class="page" id="page-',s)[1:]
todo=[]
for pg in pages:
    tab=pg[:pg.index('"')]
    for m in re.finditer(r'<details class="rec">.*?</details>',pg,re.S):
        q=re.search(r'maps/search/\?api=1&(?:amp;)?query=([^"]+)"',m.group(0))
        if q: todo.append((tab,U.unquote_plus(html.unescape(q.group(1)))))
ok=miss=0
for tab,q in todo:
    if q in geo: continue
    cands=[q]
    if ',' in q: cands.append(q.split(',')[0]+', '+q.split(',')[-1])
    hit=None
    for c in cands:
        try:
            req=R.Request('https://nominatim.openstreetmap.org/search?format=json&limit=1&q='+U.quote(c),headers={'User-Agent':'trip-page-builder/1.0'})
            r=json.load(R.urlopen(req,timeout=20))
        except Exception as e:
            r=[]
        time.sleep(1.1)
        if r:
            p=(float(r[0]['lat']),float(r[0]['lon']))
            centers=[C[tab]] if tab in C else NEXT
            if min(km(p,c2) for c2 in centers)<=(60 if tab in C else 90): hit=p;break
    geo[q]=[round(hit[0],5),round(hit[1],5)] if hit else None
    ok+=bool(hit);miss+=not hit
    json.dump(geo,open(out,'w'),ensure_ascii=False)
print('found',sum(1 for v in geo.values() if v),'missing',sum(1 for v in geo.values() if not v))
