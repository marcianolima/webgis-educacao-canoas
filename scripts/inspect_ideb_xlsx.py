#!/usr/bin/env python3
"""Inspeciona estrutura e resultados publicáveis IDEB escola (sem importação)."""
import zipfile,io,pathlib,os,openpyxl
p=pathlib.Path(os.environ["IDEB_ZIP"])
with zipfile.ZipFile(p) as z:
 names=[i for i in z.infolist() if i.filename.endswith(".xlsx")]
 if len(names)!=1:raise RuntimeError("XLSX IDEB não único")
 with z.open(names[0]) as f:
  raw=f.read()
 print("XLSX",len(raw),flush=True)
 wb=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
 print("SHEETS",[(s.title,s.max_row,s.max_column) for s in wb],flush=True)
 for s in wb:
  print("SHEET",s.title,flush=True)
  for ix,row in enumerate(s.values):
   if ix<12:print("HEADROW",ix,[str(v)[:90] if v is not None else None for v in row[:36]],flush=True)
   else:break
  found=[]
  for i,row in enumerate(s.values):
   if "4304606" in [str(v).removesuffix(".0") for v in row[:10]] or "Canoas" in [str(v) for v in row[:10]]:
    found.append([str(v)[:90] if v is not None else None for v in row[:35]])
   if i>150000:break
  print("CANOAS_MATCHES",len(found),"EXAMPLES",found[:5],flush=True)
 wb.close()
