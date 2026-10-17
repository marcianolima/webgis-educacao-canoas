#!/usr/bin/env python3
import urllib.request,urllib.parse,gzip,io,csv,collections,json
BASE="https://www.fnde.gov.br/plataforma-antonieta-de-barros-api/products/data-products"
for number in (82,56):
 print("===== PRODUCT",number,flush=True)
 req=urllib.request.Request(f"{BASE}/{number}/artifact",headers={"User-Agent":"WebGIS-Educacao-Canoas/0.4"})
 with urllib.request.urlopen(req,timeout=45) as r:data=r.read(10_000_000)
 print("compressed_bytes",len(data),"magic",data[:2],flush=True)
 text=gzip.GzipFile(fileobj=io.BytesIO(data))
 first=[text.readline() for i in range(5)]
 print("FIRST_LINES",[(x[:500].decode("utf-8","replace")) for x in first],flush=True)
 text.close()
 with gzip.GzipFile(fileobj=io.BytesIO(data)) as gz:
  count=0;matches=[]
  for raw in gz:
   count+=1
   if b'CANOAS' in raw.upper() or b'4304606' in raw or b'430460' in raw:
    matches.append(raw.decode('utf-8','replace').strip()[:1300])
   if count>1_500_000:raise RuntimeError("limite linhas excedido")
 print("ROWS",count,"CANOAS_MATCHES",len(matches),"EXAMPLE",matches[:18],flush=True)
