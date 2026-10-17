#!/usr/bin/env python3
import urllib.request,json,io,openpyxl
PKGS=[
"acesso-matriculas-e-perfil-dos-estudantes-da-educacao-basica-rio-grande-do-sul",
"infraestrutura-das-escolas-da-educacao-basica-rio-grande-do-sul",
"perfil-e-caracteristicas-da-docencia-na-educacao-basica-rio-grande-do-sul",
"indicadores-educacionais-da-educacao-basica-rio-grande-do-sul"
]
def get(url,limit=26000000):
 req=urllib.request.Request(url,headers={"User-Agent":"WebGIS-Educacao-Canoas/0.5"})
 with urllib.request.urlopen(req,timeout=55) as r:
  blob=r.read(limit+1)
 if len(blob)>limit:raise ValueError(f"Arquivo maior que {limit} bytes")
 return blob
for pkg in PKGS:
 print("PACKAGE",pkg,flush=True)
 try:
  uri="https://dados.rs.gov.br/api/3/action/package_show?id="+pkg
  source=json.loads(get(uri,3000000))
  if not source.get("success"):raise RuntimeError("CKAN unsuccessful")
  resources=source["result"]["resources"]
  print("RESOURCES",[(r["name"],r["url"][:240],r.get("size")) for r in resources],flush=True)
  for r in resources:
   if not (r.get("format") or "").upper().startswith("XLSX"):continue
   raw=get(r["url"])
   print("RESOURCE_FILE",r["name"],len(raw),flush=True)
   book=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
   for ws in book:
    print("SHEET",ws.title,"rows",ws.max_row,"cols",ws.max_column,flush=True)
    iterator=ws.iter_rows(values_only=True)
    first=[]
    for i,row in enumerate(iterator):
     if i<5:first.append([str(x)[:70] if x is not None else None for x in row[:16]])
     if i>=4:break
    print("SAMPLE",first,flush=True)
    # Scan only a small prefix for municipality token, then stop; full scan only in ETL.
    count=0;canoas=[]
    for i,row in enumerate(ws.iter_rows(values_only=True)):
     if "CANOAS" in "|".join(str(x).upper() for x in row if x is not None) or "4304606" in "|".join(str(x) for x in row if x is not None):
      count+=1
      if len(canoas)<3:canoas.append([str(x)[:70] for x in row[:14]])
     if i>60000:break
    print("CANOAS_IN_PREFIX",count,"EXAMPLES",canoas,flush=True)
   book.close()
 except Exception as exc:print("ERROR",pkg,repr(exc),flush=True)
