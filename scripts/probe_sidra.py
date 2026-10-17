#!/usr/bin/env python3
"""Validação das dimensões da tabela 9514 SIDRA, sem publicação."""
import urllib.request,json
base="https://apisidra.ibge.gov.br/values"
urls=[
 "/t/9514/n6/4304606/v/93/p/2022/c2/0/c287/all/c12762/0",
 "/t/9514/n6/4304606/v/93/p/2022/c2/0/c287/all",
 "/t/9514/n6/4304606/v/93/p/2022",
 "/t/9514/n6/4304606/p/2022",
]
for suffix in urls:
 url=base+suffix
 print("TRY",url,flush=True)
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"WebGIS-Educacao-Canoas/0.4"})
  with urllib.request.urlopen(req,timeout=25) as resp: raw=resp.read(3000000)
  obj=json.loads(raw)
  print("OK",len(obj) if isinstance(obj,list) else str(type(obj)),flush=True)
  if isinstance(obj,list):
   print("HEAD",obj[:3],flush=True)
   if len(obj)>50:
    print("AGES",[(r.get("D4N"),r.get("D5N"),r.get("D6N"),r.get("V")) for r in obj[:20]],flush=True)
 except Exception as e:print("FAIL",str(e)[:800],flush=True)
