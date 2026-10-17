#!/usr/bin/env python3
"""Inspeção somente, formato SIOPE FNDE oficial. Sem publicação de dados brutos."""
import urllib.request,urllib.parse,gzip,io,csv,json,hashlib
BASE="https://www.fnde.gov.br/plataforma-antonieta-de-barros-api/products/data-products"
for product in (19,73,55):
 print("PRODUCT",product,flush=True)
 try:
  def get(endpoint):
   req=urllib.request.Request(BASE+f"/{product}/"+endpoint,headers={"User-Agent":"WebGIS-Educacao/0.6"})
   with urllib.request.urlopen(req,timeout=42) as r:
    return r.read(32_000_001)
  meta=json.loads(get("artifact-metadata"))
  print("METADATA",str(meta)[:850],flush=True)
  if int(meta["size"])>30_000_000:print("SKIP_LARGE",meta["size"],flush=True);continue
  raw=get("artifact")
  print("BYTES",len(raw),"SHA256",hashlib.sha256(raw).hexdigest(),flush=True)
  with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
   with io.TextIOWrapper(stream,encoding="utf-8-sig",errors="replace",newline="") as text:
    hdr=text.readline()
    print("HEADER",hdr[:3000],flush=True)
    hits=[]
    delimiter=';' if hdr.count(';')>=hdr.count(',') else ','
    reader=csv.reader(text,delimiter=delimiter)
    scanned=0
    for parts in reader:
     scanned+=1
     line='|'.join(parts)
     if 'CANOAS' in line.upper() or '4304606' in line or '430460' in line:
      hits.append(parts[:28])
     if scanned>=800000:break
    print("ROWS",scanned,"CANOAS",len(hits),"SAMPLES",hits[:6],"LAST",hits[-3:],flush=True)
 except Exception as e:print("ERROR",repr(e),flush=True)
