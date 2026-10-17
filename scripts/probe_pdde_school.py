import urllib.request,re
from html.parser import HTMLParser
url="https://www.fnde.gov.br/pddeinfo/pddeinfo/escola/consultar"
req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; WebGIS-Educacao-Canoas/0.5)"})
with urllib.request.urlopen(req,timeout=40) as r:text=r.read(750000).decode("utf-8","replace");print("HTTP",r.status,"bytes",len(text),"url",r.url)
class H(HTMLParser):
 def __init__(self):super().__init__();self.tags=[]
 def handle_starttag(self,tag,attrs):
  if tag in ("form","input","select","button","script","option"):
   d=dict(attrs)
   if tag=="option" and d.get("value")==None:return
   self.tags.append((tag,{k:v for k,v in d.items() if k in ("id","name","type","value","action","method","src","onchange","onclick","placeholder")}))
p=H();p.feed(text)
print("ELEMENTS",p.tags[:140])
for word in ("Consultar","csrf","_token","codEscola","codigoEscola","2025","consulta","endpoint","api/","javax.faces","primefaces","x-csrf"):
 pos=[m.start() for m in re.finditer(word,text,re.I)]
 print("CONTEXT",word,[text[max(0,i-90):i+210].replace("\n"," ")[:300] for i in pos[:5]])
