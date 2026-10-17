#!/usr/bin/env python3
"""IDEB municipal original e SAEB estadual oficiais da SEDUC/RS (fonte INEP).

Não substitui notas municipais por resultados da rede estadual nem inventa
proficiências municipais ausentes em planilha estadual.
"""
from __future__ import annotations
import io,json,os,tempfile,urllib.request,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
import openpyxl
DATA=Path(__file__).resolve().parents[1]/"public"/"data"
URLS={
 "ideb":"https://dados.rs.gov.br/dataset/b8445a37-5a9e-4308-9709-1ac1895fb933/resource/0e99e881-3f5a-46f8-854d-b97eecd55314/download/dados_ideb.xlsx",
 "saeb":"https://dados.rs.gov.br/dataset/09d4faf9-79c4-40ce-9978-842eb40640cc/resource/6ae692a8-ca3e-46f6-ad46-51abdf4e6726/download/dados_saeb.xlsx"
}
def download(url):
 error=None
 for attempt in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (webgis-educacao-canoas/0.9)"})
   with urllib.request.urlopen(req,timeout=45) as r:raw=r.read(2_000_001)
   if not 30_000<len(raw)<2_000_000 or raw[:2]!=b"PK":raise ValueError("XLSX inválido/tamanho inesperado")
   return raw
  except Exception as e:
   error=e;time.sleep(3*(attempt+1))
 raise RuntimeError("SEDUC qualidade indisponível: "+str(error))
def records(blob,sheet):
 w=openpyxl.load_workbook(io.BytesIO(blob),read_only=True,data_only=True)
 if sheet not in w.sheetnames:raise ValueError("Aba ausente: "+sheet)
 it=iter(w[sheet].values);heads=[str(h).strip() for h in next(it)]
 data=[]
 for cells in it:
  r=dict(zip(heads,cells))
  if str(r.get("Codigo IBGE") or "").removesuffix(".0")!="4304606":continue
  year=int(r["Ano"])
  if year<2000 or year>2025:raise ValueError("Ano fora faixa")
  row={"year":year}
  for key,val in r.items():
   if key in ("Ano","Codigo IBGE","Municipio"):continue
   if val in ("","...", "-",None):row[key]=None
   else:
    try:row[key]=float(val)
    except (ValueError,TypeError):raise ValueError(f"{sheet} inválido em {year} {key}={val}")
  data.append(row)
 w.close()
 if len({v["year"] for v in data})!=len(data):raise ValueError("Ano repetido na planilha")
 return sorted(data,key=lambda a:a["year"])
def main():
 files={k:download(u) for k,u in URLS.items()}
 by={
  "Municipal":records(files["ideb"],"IDEB Municipal Mun"),
  "Estadual":records(files["ideb"],"IDEB Estadual Mun"),
  "Todas":records(files["ideb"],"IDEB Todas Mun")
 }
 for network in ("Municipal","Estadual","Todas"):
  years=[r["year"] for r in by[network]]
  if 2025 not in years or len(years)<10:raise ValueError("IDEB 2005-2025 incompleto: "+network)
 latest={n:next(x for x in by[n] if x["year"]==2025) for n in by}
 if latest["Municipal"]["AI.ideb"]!=5.3 or latest["Municipal"]["AF.ideb"]!=4.6 or latest["Estadual"]["EM.ideb"]!=4.5:
  raise ValueError("IDEB não concilia com publicações conferidas")
 if latest["Todas"]["AI.ideb"]!=5.72:raise ValueError("IDEB todas as redes incoerente")
 saeb_state=records(files["saeb"],"SAEB Estadual Mun")
 year=next(x for x in saeb_state if x["year"]==2025)
 if year["5EF.media_lp"]!=218.1 or year["5EF.media_mt"]!=227.8:
  raise ValueError("SAEB estadual Canoas 2025 não concilia")
 result={"schemaVersion":1,"municipalityCode":"4304606","updatedAt":datetime.now(timezone.utc).isoformat(),
         "sourceAgency":"INEP (séries publicadas pela SEDUC/RS)",
         "sourceURLs":URLS,"sourceSHA256":{k:hashlib.sha256(v).hexdigest() for k,v in files.items()},
         "idebByNetwork":by,"saebStateByMunicipality":saeb_state,
         "limitations":[
           "IDEB Municipal/Estadual/Todas por município: agregados por rede e etapa, não nota de cada escola.",
           "SAEB Estadual Mun: proficiências da rede estadual no município; nunca renomear como rede municipal.",
           "SAEB Todas Mun da fonte estadual não publica resultados 2025 em Canoas; dados municipais específicos ainda carecem da planilha original do INEP.",
           "IDEB para todas as redes pode incluir apenas escolas com IDEB disponível; n_escolas distinto do total de escolas Censo.",
         ]}
 DATA.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile("w",encoding="utf-8",dir=DATA,delete=False) as f:
  json.dump(result,f,ensure_ascii=False,indent=2);p=f.name
 os.replace(p,DATA/"rs_quality_official.json")
 print("IDEB 2025",latest,flush=True)
 print("SAEB Estado em Canoas 2025",year,flush=True)
if __name__=="__main__":main()
