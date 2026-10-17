#!/usr/bin/env python3
"""INEP/SEDUC-RS: rendimento, formação docente, complexidade escolar e INSE.

Agrega estritamente por município 4304606, rede, ano; não imputa números a
estabelecimentos nem divulga dados pessoais. O INSE tem último ano 2023.
"""
from __future__ import annotations
import hashlib, io, json, os, tempfile, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
import openpyxl

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"public"/"data"
CITY="4304606"
NETWORKS=("Estadual","Municipal","Federal","Privada","Todas")
FILES={
 "managementComplexity":"https://dados.rs.gov.br/dataset/8040e08b-144a-43d2-a6a7-5514a638b4f0/resource/ae5e3e52-7bed-4c48-a4d4-07d138ebb8ab/download/dados_complexidade_gestao.xlsx",
 "socioeconomic":"https://dados.rs.gov.br/dataset/8040e08b-144a-43d2-a6a7-5514a638b4f0/resource/a19c1327-63d4-4c13-b3e8-b5b48922312a/download/dados_inse.xlsx",
 "teacherAdequacy":"https://dados.rs.gov.br/dataset/8040e08b-144a-43d2-a6a7-5514a638b4f0/resource/6bd1185a-8fa6-49cc-a980-56360e302e6b/download/dados_afd.xlsx",
 "schoolFlow":"https://dados.rs.gov.br/dataset/8040e08b-144a-43d2-a6a7-5514a638b4f0/resource/0b3ea083-b442-4e4a-b679-64cb7cc6a76f/download/dados_fluxo_rendimento.xlsx",
}
PREFIX={"managementComplexity":"ICG","socioeconomic":"INSE","teacherAdequacy":"AFD","schoolFlow":"Fluxo"}
COLUMNS={
 "managementComplexity": ["total_escolas","nivel_medio",*(f"nivel_{i}.{suffix}" for i in range(1,7) for suffix in ("count","pct"))],
 "socioeconomic":["inse","mediana","nivel","n_escolas","n_alunos"],
 "teacherAdequacy":["total_escolas",*(f"{stage}.g{i}" for stage in ("ed_inf","fund_total","fund_ai","fund_af","medio") for i in range(1,6))],
 "schoolFlow":[*(f"{head}_{stage}" for head in ("aprov","reprov","aband") for stage in ("fund","fund_ai","fund_af","med"))],
}
def fetch(key:str,url:str)->bytes:
 last=None
 for attempt in range(4):
  try:
   request=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (WebGIS-Educacao-Canoas/0.6)"})
   with urllib.request.urlopen(request,timeout=70) as r:
    if r.status!=200:raise RuntimeError("HTTP "+str(r.status))
    raw=r.read(12_000_001)
   if not 40_000<len(raw)<12_000_000 or not raw.startswith(b"PK"):
    raise ValueError("XLSX incompleto ou grande demais")
   return raw
  except Exception as ex:
   last=ex
   if attempt<3:time.sleep((attempt+1)*4)
 raise RuntimeError(key+" não pôde ser obtido com HTTPS validado: "+str(last))
def number(raw,percentage=False):
 if raw is None or str(raw).strip().lower() in ("","-","...","x","nan","none"):return None
 try:
  n=float(str(raw).strip().replace(",","."))
 except ValueError:raise ValueError("Número inválido: "+repr(raw))
 if not (0<=n<1_000_000):raise ValueError("Número inválido ou negativo")
 if percentage and n>100.05:raise ValueError("Percentual >100: "+str(n))
 return round(n,3)
def extract(kind:str,data:bytes):
 book=openpyxl.load_workbook(io.BytesIO(data),read_only=True,data_only=True)
 result={}
 for network in NETWORKS:
  name=f"{PREFIX[kind]} {network} Mun"
  if name not in book.sheetnames:
   if kind=="socioeconomic" and network in ("Privada",):
    result[network]=[]
    continue
   raise ValueError("Aba ausente "+name)
  ws=book[name]; iterator=iter(ws.values)
  columns=[str(c or "").strip() for c in next(iterator)]
  for req in ("Ano","Codigo IBGE","Municipio"):
   if req not in columns:raise ValueError(name+" falta "+req)
  years={}
  for values in iterator:
   row=dict(zip(columns,values))
   if str(row["Codigo IBGE"] or "").strip().removesuffix(".0")!=CITY:continue
   year=int(number(row["Ano"]) or 0)
   if year<2005 or year>2025 or year in years:raise ValueError(name+" ano inválido/repetido")
   values={}
   for column in COLUMNS[kind]:
    raw=row.get(column)
    if column=="nivel":
     values[column]=str(raw).strip() if raw not in (None,"") else None
    else:
     pct=(column.endswith(".pct") or (kind=="teacherAdequacy" and ".g" in column) or (kind=="schoolFlow"))
     values[column]=number(raw,percentage=pct)
   years[year]={"year":year,**values}
  if not years:raise ValueError("Sem dados para Canoas: "+name)
  result[network]=[years[y] for y in sorted(years)]
 book.close()
 return result
def verify(d):
 icg=d["managementComplexity"]
 ade=d["teacherAdequacy"]
 fluxo=d["schoolFlow"]
 socio=d["socioeconomic"]
 if not all(any(y["year"]==2025 for y in icg[k]) for k in NETWORKS):raise ValueError("ICG sem 2025")
 if not all(any(y["year"]==2025 for y in ade[k]) for k in NETWORKS):raise ValueError("AFD sem 2025")
 for k in NETWORKS:
  r=next((x for x in fluxo[k] if x["year"]==2025),None)
  if r is None:raise ValueError("Rendimento sem 2025: "+k)
  for stage in ("fund","fund_ai","fund_af","med"):
   vals=[r[f"{key}_{stage}"] for key in ("aprov","reprov","aband")]
   if all(v is not None for v in vals) and abs(sum(vals)-100)>1.5:
    raise ValueError(f"Rendimento {k}/{stage} não soma 100%: {vals}")
  a=next(x for x in ade[k] if x["year"]==2025)
  for stage in ("ed_inf","fund_total","fund_ai","fund_af","medio"):
   vals=[a[f"{stage}.g{i}"] for i in range(1,6)]
   if all(x is not None for x in vals) and abs(sum(vals)-100)>2:
    raise ValueError(f"AFD {k}/{stage}: cinco grupos não somam 100%")
  c=next(x for x in icg[k] if x["year"]==2025)
  counts=[c[f"nivel_{i}.count"] for i in range(1,7)]
  if all(x is not None for x in counts) and abs(sum(counts)-(c["total_escolas"] or 0))>1:
   raise ValueError(f"ICG {k}: total de escolas difere de soma dos níveis")
 if not any(x["year"]==2023 for x in socio["Municipal"]):
  raise ValueError("INSE municipal 2023 ausente")
 if any(x["year"]>2023 for x in socio["Municipal"]):
  raise ValueError("INSE publicado após último ano observado 2023, rever arquivo")
 # ICG/AFD usam cobertura própria: não exigir mesmo denominador do Censo de
 # matrículas, nem comparar com os pontos geográficos de 2023.
def main():
 records={};sha={}
 for kind,url in FILES.items():
  raw=fetch(kind,url)
  sha[kind]=hashlib.sha256(raw).hexdigest()
  records[kind]=extract(kind,raw)
 verify(records)
 doc={"schemaVersion":1,"municipalityCode":CITY,"updatedAt":datetime.now(timezone.utc).isoformat(),
      "sourceAgency":"SEDUC/RS, processamentos de indicadores INEP","sourceURLs":FILES,
      "sourceSHA256":sha,"coverage":{
       "managementComplexity":"2013–2025 (anos efetivamente disponíveis)",
       "teacherAdequacy":"2013–2025 (anos efetivamente disponíveis)",
       "schoolFlow":"2010–2025 (anos efetivamente disponíveis)",
       "socioeconomic":"2019, 2021 e 2023; não extrapolar para 2025"},
      "notes":[
       "ICG: distribuição das escolas por níveis 1–6 e índice médio, por rede e município.",
       "AFD: proporções de docências nos grupos 1–5 por etapa e rede; NÃO número de docentes únicos.",
       "Fluxo: aprovação, reprovação e abandono são percentuais por etapa/rede/ano, não quantidades de alunos.",
       "INSE: nível socioeconômico tem último recorte 2023; escolas e estudantes representam cobertura do indicador, não universo do Censo 2025.",
       "Dados exclusivamente agregados por município e rede, não indicadores individuais de escolas."],
      **records}
 DATA.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile("w",encoding="utf8",dir=DATA,delete=False) as f:
  json.dump(doc,f,ensure_ascii=False,indent=2);temp=f.name
 os.replace(temp,DATA/"rs_indicators.json")
 for key in ("managementComplexity","teacherAdequacy","schoolFlow"):
  print(key,"Municipal 2025:",next(x for x in doc[key]["Municipal"] if x["year"]==2025),flush=True)
 print("INSE Municipal 2023",next(x for x in doc["socioeconomic"]["Municipal"] if x["year"]==2023),flush=True)
if __name__=="__main__": main()
