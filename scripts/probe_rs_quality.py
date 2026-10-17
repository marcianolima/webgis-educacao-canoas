import urllib.request,json,io,openpyxl
names=[
"indice-de-desenvolvimento-da-educacao-basica-ideb-rio-grande-do-sul",
"proficiencias-do-saeb-rio-grande-do-sul",
"resultados-e-atingimento-das-metas-educacionais-de-2025-rede-estadual-do-rio-grande-do-sul"]
for name in names:
 print("DATASET",name,flush=True)
 url="https://dados.rs.gov.br/api/3/action/package_show?id="+name
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=35) as r:obj=json.loads(r.read(500000))
  for resource in obj["result"]["resources"]:
   print("RESOURCE",resource.get("name"),resource.get("url"),"SIZE",resource.get("size"),flush=True)
   if not resource.get("url","").lower().endswith(".xlsx"):continue
   req=urllib.request.Request(resource["url"],headers={"User-Agent":"Mozilla/5.0"})
   with urllib.request.urlopen(req,timeout=50) as r:raw=r.read(22000001)
   if len(raw)>22000000:print("TOO LARGE",len(raw),flush=True);continue
   wb=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
   for sheet in wb:
    print("SHEET",sheet.title,"ROWS",sheet.max_row,"COL",sheet.max_column,flush=True)
    iterator=sheet.values
    for k,row in enumerate(iterator):
     if k<6:print("HEADER",k,[str(v)[:70] if v is not None else None for v in row[:24]],flush=True)
     else:break
    matches=[]
    for k,row in enumerate(sheet.values):
     if ("4304606" in [str(v).removesuffix(".0") for v in row[:20]] or
      any(str(v).strip().upper()=="CANOAS" for v in row[:20])):
      matches.append([str(v)[:65] if v is not None else None for v in row[:25]])
     if k>80000:break
    print("MATCH",len(matches),"FIRST",matches[:4],"LAST",matches[-3:],flush=True)
   wb.close()
 except Exception as e:print("ERROR",name,repr(e),flush=True)
