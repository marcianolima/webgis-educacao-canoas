#!/usr/bin/env python3
"""Indicadores SIOPE municipais 2018–2025 via FNDE Plataforma Antonieta.

Origem: produto público 19. São declarações bimestrais municipais, e não
despesas escola a escola. Considera apenas 6º bimestre e a última declaração
válida de cada ano. Não adiciona a SICONFI nem a repasses FNDE.
"""
from __future__ import annotations
import csv,gzip,hashlib,io,json,os,tempfile,urllib.request,datetime
from pathlib import Path
from decimal import Decimal,InvalidOperation
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"public"/"data"
BASE="https://www.fnde.gov.br/plataforma-antonieta-de-barros-api/products/data-products/19"
FIELDS=("val_desp_empe","val_desp_liqu","val_desp_paga","vl_desp_empe_edu","vl_desp_liqu_edu","vl_desp_paga_edu")
def fetch():
 req=urllib.request.Request(BASE+"/artifact-metadata",headers={"User-Agent":"WebGIS-Educacao-Canoas/0.7"})
 with urllib.request.urlopen(req,timeout=45) as r:meta=json.loads(r.read(9000))
 maxsize=30_000_000
 if not 50000<int(meta["size"])<maxsize:raise ValueError("SIOPE arquivo fora dos limites")
 req=urllib.request.Request(BASE+"/artifact",headers={"User-Agent":"WebGIS-Educacao-Canoas/0.7"})
 with urllib.request.urlopen(req,timeout=90) as r:raw=r.read(maxsize+1)
 if len(raw)!=int(meta["size"]) or raw[:2]!=b"\x1f\x8b":raise ValueError("SIOPE comprimido inválido")
 return raw,meta
def money(raw):
 if raw is None or not raw.strip():return None
 try:v=Decimal(raw.strip().replace(",","."))
 except InvalidOperation:raise ValueError("SIOPE monetário inválido: "+repr(raw))
 if not v.is_finite() or v<0 or v>10_000_000_000:raise ValueError("SIOPE monetário fora de limites")
 return float(v)
def extract(blob):
 output={}
 with gzip.GzipFile(fileobj=io.BytesIO(blob)) as gz:
  with io.TextIOWrapper(gz,encoding="utf-8-sig",errors="strict",newline="") as f:
   reader=csv.DictReader(f,delimiter=";")
   required={"tipo","num_ano","num_peri","cod_uf","sig_uf","cod_muni","nom_muni","dat_decl"}|set(FIELDS)
   if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
    raise ValueError("Layout SIOPE incompatível: "+str(required-set(reader.fieldnames or [])))
   for line in reader:
    if line["tipo"]!="Municipal" or line["cod_muni"]!="430460" or line["sig_uf"]!="RS" or line["nom_muni"].upper()!="CANOAS":continue
    if line["num_peri"]!="6":continue
    year=int(line["num_ano"])
    if not 2010<=year<=2025:continue
    declaration=line["dat_decl"].strip()
    if not declaration:raise ValueError("SIOPE: declaração sem data")
    try:timestamp=datetime.datetime.fromisoformat(declaration.replace("Z","+00:00"))
    except ValueError:
     print("SIOPE_LAYOUT_DEBUG",year,"fieldnames",len(reader.fieldnames or []),"row_keys",len(line),
           "dat_decl",repr(declaration),"sample",{key:line.get(key) for key in ("num_ano","num_peri","num_reci","cod_muni","dat_decl","val_desp_empe","vl_desp_empe_edu")},flush=True)
     raise ValueError("SIOPE data de declaração inválida; é necessário revisar esquema da fonte")
    metrics={k:money(line[k]) for k in FIELDS}
    if not all(metrics[k] is not None for k in ("vl_desp_empe_edu","vl_desp_liqu_edu")):
     raise ValueError("SIOPE: sem valores educacionais")
    row={"year":year,"period":6,"declaredAt":declaration,
         "education":{"committedBRL":metrics["vl_desp_empe_edu"],
                      "liquidatedBRL":metrics["vl_desp_liqu_edu"],
                      "paidBRL":metrics["vl_desp_paga_edu"]}}
    old=output.get(year)
    if old is None or timestamp>datetime.datetime.fromisoformat(old["declaredAt"].replace("Z","+00:00")):
     output[year]=row
 if 2025 not in output:raise ValueError("SIOPE municipal 2025 6º bimestre ausente")
 if not 100_000_000<output[2025]["education"]["committedBRL"]<2_000_000_000:
  raise ValueError("SIOPE despesa de educação 2025 fora de faixa plausível")
 return [output[y] for y in sorted(output)]
def main():
 raw,meta=fetch()
 records=extract(raw)
 out={"schemaVersion":1,"municipalityCode":"4304606","source":"https://www.fnde.gov.br/plataforma-antonieta-de-barros/dados/produtos-de-dados/visualizar/19",
      "api":BASE+"/artifact","sourceSHA256":hashlib.sha256(raw).hexdigest(),"fndeMeta":meta,
      "definition":"Declarações SIOPE do 6º bimestre, selecionada a última declaração de cada exercício. Despesas próprias informadas no campo vl_desp_*_edu. Não somar com SICONFI, FUNDEB, PNAE ou PDDE. Valores nominais.",
      "years":records}
 DATA.mkdir(exist_ok=True,parents=True)
 with tempfile.NamedTemporaryFile("w",encoding="utf8",dir=DATA,delete=False) as f:
  json.dump(out,f,ensure_ascii=False,indent=2);name=f.name
 os.replace(name,DATA/"siope.json")
 print("SIOPE anos",len(records),"2025:",next(x for x in records if x["year"]==2025),flush=True)
if __name__=="__main__":main()
