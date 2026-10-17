#!/usr/bin/env python3
"""List field names IDEB 2025 INEP, without publishing unverified results."""
import pathlib,os,zipfile,io,openpyxl
z=pathlib.Path(os.environ["IDEB_ZIP"])
with zipfile.ZipFile(z) as arc:
 names=[x for x in arc.infolist() if x.filename.endswith(".xlsx")]
 assert len(names)==1
 with arc.open(names[0]) as f:
  wb=openpyxl.load_workbook(io.BytesIO(f.read()),read_only=True,data_only=True)
  for sheet in wb:
   it=iter(sheet.values)
   for i,row in enumerate(it):
    if i==9:
     print("COLUMNS",len(row),list(enumerate(row)),flush=True)
     break
   count=0
   for row in it:
    if str(row[1] or "").replace(".0","")=="4304606":
     count+=1
     if count<=4:
      print("CANOAS",row[3],row[4],"TAIL",list(enumerate(row))[-34:],flush=True)
   print("CITY_MATCHES",count,flush=True)
  wb.close()
