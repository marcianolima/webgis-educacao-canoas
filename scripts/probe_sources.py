"""Diagnóstico de fontes públicas: descobre links oficiais sem download integral."""
from html.parser import HTMLParser
import re, urllib.request, urllib.parse, ssl, json, time, sys

SOURCES={
 "inep_censo":"https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar",
 "ideb_2025":"https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados/2005-2025",
 "saeb_2025":"https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/saeb/resultados/2025",
 "saeb_2023":"https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/saeb/resultados/2023",
 "mec_pdde":"https://dadosabertos.mec.gov.br/sala-de-recursos-pdde",
}
class Links(HTMLParser):
 def __init__(self): super().__init__();self.links=[];self.cur=None
 def handle_starttag(self,t,attrs):
  if t=="a":
   self.cur=dict(attrs).get("href");self.txt=""
 def handle_data(self,data):
  if self.cur is not None:self.txt+=data
 def handle_endtag(self,t):
  if t=="a" and self.cur:
   self.links.append((self.txt.strip(),self.cur));self.cur=None

def load(url,method="GET"):
 req=urllib.request.Request(url,method=method,headers={"User-Agent":"Mozilla/5.0 (compatible; WebGIS-Educacao-Canoas/0.3)","Accept":"text/html,*/*"})
 with urllib.request.urlopen(req,timeout=18) as r:
  return r.read(700000).decode("utf-8",errors="replace"),r.status,r.geturl(),r.headers.get("Content-Type","")

for name,url in SOURCES.items():
 print("\n=== SOURCE",name,url,flush=True)
 try:
  body,status,final,ctype=load(url)
  p=Links();p.feed(body)
  print("STATUS",status,"FINAL",final,"content_type",ctype,"links",len(p.links))
  selected=[(t,u) for t,u in p.links if
             "download.inep.gov.br" in u or "apigatewayolinda" in u or
             "s3.amazonaws.com" in u or "dadosabertos" in u or "ideb.inep.gov.br" in u]
  for text,url in selected[:45]:
   if name=="inep_censo" and "2025" not in text:continue
   print("LINK",repr(text[:110]),urllib.parse.urljoin(final,url)[:320])
 except Exception as ex: print("ERROR",type(ex).__name__,str(ex)[:400],flush=True)
