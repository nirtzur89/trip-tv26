# Inlines the booking screenshots into the page so they are encrypted with it.
import re,base64,sys,os
src,dst,assets=sys.argv[1:4]
s=open(src,encoding='utf-8').read()
def f(m):
    p=os.path.join(assets,m.group(1))
    if not os.path.exists(p): return m.group(0)
    return 'src="data:image/jpeg;base64,'+base64.b64encode(open(p,'rb').read()).decode()+'"'
s=re.sub(r'src="(img/[^"]+\.jpg)"',f,s)
open(dst,'w',encoding='utf-8').write(s)
