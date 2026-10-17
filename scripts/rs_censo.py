#!/usr/bin/env python3
"""Censo Escolar por MUNICÍPIO/rede, extraído de arquivos oficiais SEDUC-RS.

Arquivo derivado dos microdados INEP. Não contém indicadores individuais por escola.
"""
from __future__ import annotations
import hashlib,io,json,os,tempfile,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
import openpyxl
DATA=Path(__file__).resolve().parents[1]/"public"/"data"
CITY="4304606";NETWORKS=("Estadual","Municipal","Federal","Privada","Todas")
URLS={
 "enrollments":"https://dados.rs.gov.br/dataset/af11aa7d-0016-4b49-b73b-655f543334f7/resource/9c23921d-bde4-48ed-bbb9-2fe5b5393636/download/dados_acesso_matriculas.xlsx",
 "infrastructure":"https://dados.rs.gov.br/dataset/5ab85ab2-2f01-44b8-bae0-53b24e74e574/resource/949999fd-9492-44fb-9c8b-128d6a301ba2/download/dados_infraestrutura.xlsx"
}
def download(url):
 err=None
 for attempt in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (WebGIS-Educacao-Canoas/0.5)","Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})
   with urllib.request.urlopen(req,timeout=60) as r:blob=r.read(14_000_001)
   if not 100000<len(blob)<14_000_000 or not blob.startswith(b"PK"):
    raise ValueError("Arquivo XLSX não válido/tamanho suspeito")
   return blob
  except Exception as e:
   err=e
   print(f"::warning::Tentativa {attempt+1}: {e}",flush=True)
   if attempt<3:time.sleep(3*(attempt+1))
 raise RuntimeError("Arquivo SEDUC/RS inacessível: "+str(err))
def number(x,integer=False):
 if x is None or str(x).strip() in ("","-","...","X"):return None
 n=float(str(x).replace(",","."))
 if not 0<=n<=2_000_000:raise ValueError("Valor de indicador fora do intervalo: "+repr(x))
 if integer and not n.is_integer():raise ValueError("Indicador inteiro fracionário")
 return int(n) if integer else round(n,2)
def extract(blob,prefix):
 b=openpyxl.load_workbook(io.BytesIO(blob),read_only=True,data_only=True)
 output={}
 for network in NETWORKS:
  sheetname=prefix+" "+network+" Mun"
  if sheetname not in b.sheetnames:raise ValueError("Aba obrigatória SEDUC ausente: "+sheetname)
  ws=b[sheetname];i=iter(ws.values)
  header=[str(s or "").strip() for s in next(i)]
  required=["Ano","Codigo IBGE","escolas"]
  if not all(x in header for x in required):raise ValueError("Cabeçalho incompleto")
  if prefix=="Acesso" and not all(x in header for x in ["mat_total","mat_infantil","mat_fundamental","mat_medio","mat_eja"]):
   raise ValueError("Colunas de matrícula ausentes")
  if prefix=="Infra" and not all(x in header for x in ["Acesso a Internet (%)","Biblioteca (%)","Quadra de Esportes (%)"]):
   raise ValueError("Colunas de infraestrutura ausentes")
  years={}
  for values in i:
   row=dict(zip(header,values))
   if str(row.get("Codigo IBGE") or "").strip().removesuffix(".0")!=CITY:continue
   year=number(row["Ano"],integer=True)
   if year is None or year<2010 or year>2025:raise ValueError("Ano inesperado")
   if year in years:raise ValueError(f"{network}: ano duplicado {year}")
   if prefix=="Acesso":
    required_cols=["mat_total","mat_infantil","mat_fundamental","mat_fund_ai","mat_fund_af","mat_medio","mat_eja"]
    metrics={k:number(row.get(k),integer=True) for k in required_cols}
    if any(metrics[k] is None for k in required_cols):raise ValueError(f"{network}/{year}: matrícula obrigatória ausente")
    if metrics["mat_fund_ai"]+metrics["mat_fund_af"]!=metrics["mat_fundamental"]:
     raise ValueError(f"{network}/{year}: anos iniciais e finais não conciliam")
    if sum(metrics[k] for k in ("mat_infantil","mat_fundamental","mat_medio","mat_eja"))>metrics["mat_total"]:
     raise ValueError(f"{network}/{year}: etapas maiores que matrículas básicas")
    metrics.update({"schools":number(row["escolas"],integer=True)})
   else:
    cols=["Acesso a Internet (%)","Banda Larga (%)","Computador (%)",
      "Lab. Informatica (%)","Biblioteca (%)","Biblioteca ou Sala de Leitura (%)",
      "Lab. Ciencias (%)","Quadra de Esportes (%)","Acessibilidade (%)",
      "Banheiro PNE (%)","Internet para alunos (%)"]
    metrics={"schools":number(row["escolas"],integer=True)}
    for col in cols:
     if col in header:
      v=number(row.get(col))
      if v is not None and v>100:raise ValueError("Percentual acima de 100")
      metrics[col]=v
   years[year]={"year":year,**metrics}
  if len(years)<14 or 2025 not in years:raise ValueError(f"{network}: cobertura 2025 ausente ({len(years)} exercícios)")
  output[network]=[years[k] for k in sorted(years)]
 b.close()
 return output
def reconciled(matrix):
 yearsets={network:{v["year"] for v in matrix[network]} for network in NETWORKS}
 years=sorted(set.intersection(*yearsets.values()))
 if len(years)<14 or 2025 not in years:raise ValueError("Interseção de exercícios das redes insuficiente")
 for year in years:
  by={name:next(x for x in matrix[name] if x["year"]==year) for name in NETWORKS}
  for col in ("schools","mat_total"):
   total=by["Todas"][col]
   sums=sum(by[name][col] for name in NETWORKS[:-1])
   if total!=sums:
    raise ValueError(f"Total SEDUC 2025 não reconciliado, {year}/{col}: {total} ≠ {sums}")
def main():
 payload={};hashes={}
 for name,url in URLS.items():
  data=download(url);hashes[name]=hashlib.sha256(data).hexdigest()
  payload[name]=extract(data,"Acesso" if name=="enrollments" else "Infra")
 reconciled(payload["enrollments"])
 row2025={k:next(r for r in payload["enrollments"][k] if r["year"]==2025) for k in NETWORKS}
 out={"schemaVersion":1,"municipalityCode":CITY,"updatedAt":datetime.now(timezone.utc).isoformat(),
  "reference":"2010–2025","scope":"MUNICÍPIO por rede de ensino, não por escola",
  "sourceAgency":"SEDUC/RS, com base no Censo Escolar do INEP",
  "sourceURLs":URLS,"sha256":hashes,
  "notes":["Séries de matrículas por local da escola (não residentes por domicílio).",
           "Dados de 2025 por município e rede; não atribuir a escola selecionada.",
           "Matrículas não são estudantes únicos; indicadores de infraestrutura são percentuais de escolas.",
           "Infraestrutura e matrículas podem ter denominadores distintos conforme arquivo/metodologia."],
  "enrollments":payload["enrollments"],"infrastructure":payload["infrastructure"]}
 DATA.mkdir(exist_ok=True,parents=True)
 with tempfile.NamedTemporaryFile("w",encoding="utf8",dir=DATA,delete=False) as f:
  json.dump(out,f,ensure_ascii=False,indent=2);temp=f.name
 os.replace(temp,DATA/"rs_censo_municipal.json")
 print("SEDUC CENSO 2025",row2025,flush=True)
 print("INTEGRIDADE",hashes,flush=True)
if __name__=="__main__":main()
