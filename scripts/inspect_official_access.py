#!/usr/bin/env python3
"""Descobrir apenas endpoints oficiais HTTPS, sem ignorar certificados nem baixar PII."""
import urllib.request,urllib.parse,re,json,ssl,html
from html.parser import HTMLParser
PAGES=[
"https://www.fnde.gov.br/plataforma-antonieta-de-barros/dados/produtos-de-dados/visualizar/82",
"https://www.fnde.gov.br/plataforma-antonieta-de-barros/dados/produtos-de-dados/visualizar/56",
"https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar",
"https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/inep-data/catalogo-de-escolas/",
]
class P(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.scripts=[]
 def handle_starttag(self,tag,attr):
  a=dict(attr)
  if tag=="a" and a.get("href"):self.links.append((a.get("href"),a.get("download"),a.get("title")))
  if tag=="script" and a.get("src"):self.scripts.append(a["src"])
for page in PAGES:
 print("PAGE",page,flush=True)
 try:
  req=urllib.request.Request(page,headers={"User-Agent":"Mozilla/5.0","Accept":"text/html"})
  with urllib.request.urlopen(req,timeout=25) as r:
   data=r.read(900000).decode('utf-8','replace')
   print("STATUS",r.status,"URL",r.url,"SIZE",len(data),flush=True)
  p=P();p.feed(data)
  print("SCRIPTS",p.scripts[-18:],flush=True)
  print("LINKS",[(v,t) for v,t,d in p.links if "2025" in str(v)+str(d) or "gz" in str(v) or "download" in str(v).lower()][:20],flush=True)
  if "inep.gov.br" in page:
   print("INEP_2025",[(v,d) for v,t,d in p.links if "2025" in str(d)+str(v) or "2025" in data[max(0,data.find(v)-300):data.find(v)+400]][:12],flush=True)
  for term in ["PNAE_repasses","exportar artefato","Exportar artefato","artefato","/api/","download", "__NEXT_DATA__","files/","txt.gz"]:
   indexes=[m.start() for m in re.finditer(re.escape(term),data,re.I)][:3]
   print("CONTEXT",term,[re.sub(r'\\s+',' ',data[max(0,i-130):i+300])[:430] for i in indexes],flush=True)
  print("INLINE_URL",list(dict.fromkeys(re.findall(r'https?[^"\\s<>]{4,180}',data)))[:15],flush=True)
 except Exception as ex:print("FAIL",repr(ex),flush=True)
