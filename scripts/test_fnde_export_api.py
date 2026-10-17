import json,urllib.request,urllib.error
BASE="https://www.fnde.gov.br/plataforma-antonieta-de-barros-api"
for identifier in (82,56,80):
 for suffix in (f"/products/data-products/{identifier}/artifact-metadata",f"/products/data-products/{identifier}/artifact"):
  url=BASE+suffix
  try:
   req=urllib.request.Request(url,headers={"Accept":"application/json","User-Agent":"WebGIS-Educacao-Canoas/0.4"})
   with urllib.request.urlopen(req,timeout=25) as resp:
    print("RESP",url,"status",resp.status,"type",resp.headers.get("Content-Type"),"length",resp.headers.get("Content-Length"),"final",resp.url,flush=True)
    print("FIRST",resp.read(600),flush=True)
  except Exception as ex:print("ERROR",url,repr(ex)[:300],flush=True)
