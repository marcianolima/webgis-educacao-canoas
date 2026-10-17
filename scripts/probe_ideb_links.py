import urllib.request,re,html
from html.parser import HTMLParser
URL="https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados/2005-2025"
class L(HTMLParser):
 def __init__(self):super().__init__();self.items=[];self.href=None;self.text=""
 def handle_starttag(self,tag,atts):
  if tag=="a":self.href=dict(atts).get("href");self.text=""
 def handle_data(self,value):
  if self.href is not None:self.text+=value
 def handle_endtag(self,tag):
  if tag=="a" and self.href:
   self.items.append((self.text.strip(),self.href));self.href=None
with urllib.request.urlopen(urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0"}),timeout=30) as r:
 text=r.read(900000).decode("utf-8","replace")
p=L();p.feed(text)
for title,url in p.items:
 if "download.inep.gov.br" in url:
  print("ITEM",title[:100],url[:450],flush=True)
