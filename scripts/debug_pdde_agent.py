import importlib.util,urllib.request,urllib.parse
from bs4 import BeautifulSoup
src=importlib.util.spec_from_file_location("collector","scripts/fnde_pdde.py")
m=importlib.util.module_from_spec(src);src.loader.exec_module(m)
code="43170102"
for useragent in ("WebGIS-Educacao-Canoas/0.5 (consultas públicas municipais)","Mozilla/5.0 WebGIS-Canoas/0.5","Mozilla/5.0"):
 q=urllib.parse.urlencode({"ano":2025,"co_escola":code,"consultar":"Consultar"})
 req=urllib.request.Request(m.SOURCE+"?"+q,headers={"User-Agent":useragent,"Accept":"text/html"})
 with urllib.request.urlopen(req,timeout=30) as resp:
  data=resp.read(150000).decode("utf-8","replace")
 soup=BeautifulSoup(data,"html.parser")
 print("AGENT",useragent,"len",len(data),"headers",str(soup.title)[:120],"schoolLinks",len(soup.select(".govbr-school-link-title")),"total geral",data.count("TOTAL GERAL"),"school name",data.count("ARTHUR OSCAR"))
 print("PARSED",m.parse(data,code))
