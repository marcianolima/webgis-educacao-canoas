import urllib.request,urllib.parse,re,html
from html.parser import HTMLParser
BASE="https://www.fnde.gov.br/pddeinfo/pddeinfo/escola/consultar"
for year,inep in [(2025,"43170102"),(2024,"43170102"),(2025,"43037836")]:
 qs=urllib.parse.urlencode({"ano":year,"co_escola":inep,"consultar":"Consultar"})
 url=BASE+"?"+qs
 print("TRY",year,inep,flush=True)
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 WebGIS-Canoas/0.5"})
  with urllib.request.urlopen(req,timeout=35) as r:
   text=r.read(300_000).decode("utf-8","replace")
   print("HTTP",r.status,"LEN",len(text),"URL",r.url,flush=True)
  for w in ("Dados da Escola","Resultado da Consulta","Valor Liberado","Repasses","Valor Pago","LIBERADO","ANO","EMEF ARTHUR","Nenhuma escola","não encontrado","Erro"):
   hits=list(re.finditer(re.escape(w),text,re.I))
   print("MATCH",w,len(hits),flush=True)
   for m in hits[-3:]:
    s=re.sub(r'<[^>]+>',' ',text[max(0,m.start()-180):m.end()+310])
    print("CTX",html.unescape(re.sub(r"\s+"," ",s))[:400],flush=True)
  print("RESULT_TABLES",[(m.start(),text[m.start():m.start()+160]) for m in list(re.finditer("<table",text,re.I))[-8:]],flush=True)
 except Exception as exc:print("FAIL",repr(exc),flush=True)
