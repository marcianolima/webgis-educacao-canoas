#!/usr/bin/env python3
"""IDEB 2005–2025 por estabelecimento (INEP oficial), 3 etapas.
Os arquivos fornecem resultados somente para escolas com divulgação; valores ND
ou '-' são NULL, nunca zero. Nenhum dado identificável de estudantes é coletado.
"""
from __future__ import annotations
import io,json,os,re,tempfile,zipfile,hashlib
from pathlib import Path
from datetime import datetime,timezone
import openpyxl

DATA=Path(__file__).resolve().parents[1]/"public"/"data"
STAGES=("fundamentalInitial","fundamentalFinal","highSchool")
FILES={
 "fundamentalInitial":"divulgacao_anos_iniciais_escolas_2025.zip",
 "fundamentalFinal":"divulgacao_anos_finais_escolas_2025.zip",
 "highSchool":"divulgacao_ensino_medio_escolas_2025.zip",
}
ALIASES={
 "fundamentalInitial":"Anos iniciais do ensino fundamental (5º ano)",
 "fundamentalFinal":"Anos finais do ensino fundamental (9º ano)",
 "highSchool":"Ensino médio",
}
YEARS=list(range(2005,2026,2))
def num(value,lo,hi):
 if value is None or isinstance(value,bool):return None
 if str(value).strip().upper() in ("","-","ND","...","X","NAN"):return None
 try:f=float(value)
 except (TypeError,ValueError):raise ValueError("INEP IDEB inválido: "+str(value))
 if not lo<=f<=hi:raise ValueError("INEP IDEB fora da escala esperada: "+str(f))
 return round(f,6)
def load(stage,path):
 if not path.is_file() or not zipfile.is_zipfile(path):raise ValueError("ZIP IDEB ausente/inválido")
 with zipfile.ZipFile(path) as z:
  members=[m for m in z.infolist() if m.filename.lower().endswith(".xlsx")]
  if len(members)!=1:raise ValueError("IDEB XLSX não único no ZIP "+stage)
  with z.open(members[0]) as inp:book=openpyxl.load_workbook(io.BytesIO(inp.read()),read_only=True,data_only=True)
  try:
   if len(book.worksheets)!=1:raise ValueError("IDEB número inesperado de abas")
   it=iter(book.worksheets[0].values)
   header=None
   for i,row in enumerate(it):
    if i==9:
     header=list(row);break
   if not header or not all(k in header for k in ("CO_MUNICIPIO","ID_ESCOLA","REDE","VL_OBSERVADO_2025")):
    raise ValueError("IDEB campo obrigatório ausente")
   lookup={str(k):i for i,k in enumerate(header) if k}
   found={}
   for row in it:
    city=str(row[lookup["CO_MUNICIPIO"]] or "").removesuffix(".0").strip()
    if city!="4304606":continue
    code=str(row[lookup["ID_ESCOLA"]] or "").removesuffix(".0")
    if not re.fullmatch(r"\d{8}",code):raise ValueError("INEP inválido no IDEB escola")
    if code in found:raise ValueError("IDEB duplicação de escola "+code)
    results=[]
    for year in YEARS:
     key="VL_OBSERVADO_"+str(year)
     if key not in lookup:raise ValueError("Série histórica incompleta")
     ideb=num(row[lookup[key]],0,10)
     if ideb is not None:results.append({"year":year,"ideb":ideb})
    key5={
     "ideb":num(row[lookup["VL_OBSERVADO_2025"]],0,10),
     "portugueseScore":num(row[lookup["VL_NOTA_PORTUGUES_2025"]],0,500),
     "mathScore":num(row[lookup["VL_NOTA_MATEMATICA_2025"]],0,500),
     "performanceScore":num(row[lookup["VL_NOTA_MEDIA_2025"]],0,10),
     "promotionFactor":num(row[lookup["VL_INDICADOR_REND_2025"]],0,1),
    }
    found[code]={"inep":code,"name":str(row[lookup["NO_ESCOLA"]] or "").strip()[:220],
      "network":str(row[lookup["REDE"]] or "").strip(),"stage":stage,
      "stageLabel":ALIASES[stage],"year":2025,"current":key5,"history":results,
      "has2025Result":key5["ideb"] is not None}
   if len(found)<10:raise ValueError("IDEB Cobertura escolar de Canoas insuficiente")
   return found
  finally:book.close()
def main():
 original={}
 for stage in STAGES:
  loc=os.environ.get("INEP_IDEB_"+stage.upper()+"_ZIP")
  if not loc:raise EnvironmentError("ZIP IDEB não apontado para "+stage)
  p=Path(loc)
  digest=hashlib.sha256()
  with p.open("rb") as f:
   for part in iter(lambda:f.read(4*1024*1024),b""):digest.update(part)
  values=load(stage,p)
  original[stage]={"source":"https://download.inep.gov.br/ideb/resultados/"+FILES[stage],
                   "sha256":digest.hexdigest(),"totalCanoas":len(values),
                   "withIDEB2025":sum(1 for x in values.values() if x["has2025Result"])}
  print("IDEB 2025",stage,original[stage],flush=True)
  if stage=="fundamentalInitial" and values.get("43007520",{}).get("current",{}).get("ideb")!=7.3:
   raise ValueError("Escola de referência não confere com fonte original (INEP 43007520)")
  original[stage]["records"]=values
 if sum(meta["withIDEB2025"] for meta in original.values())<55:
  raise ValueError("Cobertura divulgada de IDEB 2025 suspeita")
 doc={"schemaVersion":1,"municipalityCode":"4304606","year":2025,
      "updatedAt":datetime.now(timezone.utc).isoformat(),
      "sourceAgency":"INEP IDEB 2025 V2, arquivos oficiais por estabelecimento",
      "stages":original,
      "notes":[
       "O resultado do IDEB/SAEB por escola só é disponibilizado quando atende às condições de divulgação do INEP.",
       "Escolas com notas ausentes, ND e '–' permanecem sem nota, não zero.",
       "Notas SAEB de Português e Matemática constam como proficiências; VL_NOTA_MEDIA é a nota padronizada em escala 0–10.",
       "IDEB não tem comparabilidade de notas entre etapas sem contextualização.",
       "Arquivos originais ZIP/XLSX não são publicados; apenas dados agregados por estabelecimento.",
      ]}
 DATA.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile("w",encoding="utf8",dir=DATA,delete=False) as f:
  json.dump(doc,f,ensure_ascii=False,indent=2);p=f.name
 os.replace(p,DATA/"ideb_schools.json")
 print("IDEB escolar publicado com rastreabilidade",sum(x["withIDEB2025"] for x in original.values()),flush=True)
if __name__=="__main__":main()
