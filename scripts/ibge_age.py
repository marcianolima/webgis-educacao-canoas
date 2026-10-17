#!/usr/bin/env python3
"""Perfil etário oficial de Canoas, Censo IBGE 2022, SIDRA tabela 9514.

População por residência, não matrículas por escola. Reconciliada contra
total municipal e faixas quinquenais para detectar dupla contagem.
"""
from __future__ import annotations
import json,os,urllib.request,tempfile,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"public"/"data"
URL="https://apisidra.ibge.gov.br/values/t/9514/n6/4304606/v/93/p/2022/c2/0/c287/all"
GROUPS={
 "0–3 anos":list(range(0,4)),
 "4–5 anos":[4,5],
 "6–14 anos":list(range(6,15)),
 "15–17 anos":[15,16,17],
 "18–24 anos":list(range(18,25)),
}
def fetch():
 error=None
 for n in range(3):
  try:
   req=urllib.request.Request(URL,headers={"User-Agent":"WebGIS-Educacao-Canoas/0.4","Accept":"application/json"})
   with urllib.request.urlopen(req,timeout=30) as resp:
    raw=resp.read(2_000_001)
   if len(raw)>2_000_000:raise ValueError("SIDRA: resposta muito grande")
   return json.loads(raw)
  except Exception as ex:
   error=ex
   if n<2:time.sleep(2**n)
 raise RuntimeError("SIDRA indisponível: "+str(error))
def parse(rows):
 if not isinstance(rows,list) or len(rows)<100:raise ValueError("SIDRA: dados incompletos")
 ages={}
 group_totals={}
 total=None
 for row in rows[1:]:
  if row.get("D1C")!="4304606" or row.get("D3C")!="2022" or row.get("D2C")!="93":raise ValueError("SIDRA: município/período/variável incorretos")
  if row.get("D6N")!="Total":continue
  label=row.get("D5N","")
  value=row.get("V")
  if not value or not value.isdigit():continue
  count=int(value)
  if label=="Total":total=count
  elif label=="Menos de 1 ano":ages[0]=count
  elif label.endswith(" ano") and label[:-4].isdigit():ages[int(label[:-4])]=count
  elif label.endswith(" anos") and label[:-5].isdigit():ages[int(label[:-5])]=count
  elif label.endswith(" anos"):group_totals[label]=count
 if total!=347657:raise ValueError(f"SIDRA: Censo 2022 divergente: {total}")
 if set(range(25))-ages.keys():raise ValueError("SIDRA: idades simples ausentes: "+str(set(range(25))-ages.keys()))
 for a,b in [(0,4),(5,9),(10,14),(15,19),(20,24)]:
  k=f"{a} a {b} anos"
  if k not in group_totals or sum(ages[i] for i in range(a,b+1))!=group_totals[k]:
   raise ValueError("SIDRA: reconciliação quinquenal falhou: "+k)
 groups={key:sum(ages[i] for i in values) for key,values in GROUPS.items()}
 groups["0–17 anos"]=sum(ages[i] for i in range(18))
 return {"schemaVersion":1,"municipalityCode":"4304606","year":2022,
         "source":URL,"updatedAt":datetime.now(timezone.utc).isoformat(),
         "totalPopulation":total,
         "ageGroups":groups,
         "ageSingles":{str(i):ages[i] for i in range(25)},
         "definition":"População residente por idade simples, Censo Demográfico 2022 (SIDRA 9514). Residentes do município, não matrículas em unidades escolares; nenhuma projeção para 2026.",
         "coverage":"Censo 2022; residentes de Canoas/RS"}
def main():
 out=parse(fetch());DATA.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile("w",encoding="utf8",dir=DATA,delete=False) as f:
  json.dump(out,f,ensure_ascii=False,indent=2);name=f.name
 os.replace(name,DATA/"ibge_age.json")
 print("IBGE SIDRA 9514 VALIDADO:",out["ageGroups"],"total",out["totalPopulation"])
if __name__=="__main__":main()
