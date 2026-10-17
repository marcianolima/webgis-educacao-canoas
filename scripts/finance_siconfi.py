#!/usr/bin/env python3
"""DCA SICONFI, fonte federal primária, por FUNÇÃO orçamentária.

Nunca soma empenhadas/liquidadas/pagas nem subfunções ao total; nunca atribui
valores do município às escolas. Em caso de falha mantém snapshot anterior.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json, os, time, urllib.parse, urllib.request, tempfile, math

DATA=Path(__file__).resolve().parents[1] / "public" / "data"
ENDPOINT="https://apidatalake.tesouro.gov.br/ords/cdwhprd/siconfi/tt/dca"
CITY=4304606
ANNEX="DCA-Anexo I-E"
COLUMNS={"Despesas Empenhadas":"committed","Despesas Liquidadas":"liquidated","Despesas Pagas":"paid"}
CODES={"12 - Educação":"education","12.365 - Educação Infantil":"earlyChildhood","12.367 - Educação Especial":"specialEducation"}
def get_data(year:int)->list[dict]:
    query=urllib.parse.urlencode({"an_exercicio":year,"id_ente":CITY,"no_anexo":ANNEX})
    url=ENDPOINT+"?"+query
    error=None
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={"Accept":"application/json","User-Agent":"WebGIS-Educacao-Canoas/0.3"})
            with urllib.request.urlopen(req, timeout=40) as res:
                if res.status!=200:raise RuntimeError("HTTP "+str(res.status))
                blob=res.read(5_000_001)
            if len(blob)>5_000_000:raise ValueError("Resposta DCA grande demais, revisar paginação")
            obj=json.loads(blob)
            if obj.get("hasMore") or not isinstance(obj.get("items"),list):
                raise ValueError("SICONFI retornou dados paginados/incompletos")
            return obj["items"]
        except Exception as exc:
            error=exc
            if attempt<2:time.sleep(2**attempt)
    raise RuntimeError(f"Não foi possível ler SICONFI DCA {year}: {error}")

def parse(year:int, items:list[dict])->dict:
    if len(items)<50:raise ValueError("SICONFI: anexo incompleto")
    found={}
    for row in items:
        if int(row.get("cod_ibge") or 0)!=CITY or int(row.get("exercicio") or 0)!=year or row.get("anexo")!=ANNEX:raise ValueError("SICONFI: mistura de município, ano ou anexo")
        if row.get("cod_conta")!="TotalDespesas" or row.get("rotulo")!="Total Geral da Despesa por Função":continue
        c=COLUMNS.get(row.get("coluna"))
        a=CODES.get(row.get("conta"))
        if c is None or a is None:continue
        val=row.get("valor")
        if not isinstance(val,(float,int)) or not math.isfinite(val) or val<0 or val>10_000_000_000:raise ValueError("Valor monetário inválido")
        key=(a,c)
        if key in found:raise ValueError("SICONFI: duplicação de indicador "+str(key))
        found[key]=round(float(val),2)
    for col in COLUMNS.values():
        if ("education",col) not in found:raise ValueError("SICONFI não contém função 12 na coluna "+col)
    for col in COLUMNS.values():
        total=found["education",col]
        for sub in ("earlyChildhood","specialEducation"):
            if found.get((sub,col),0)>total:raise ValueError("Subfunção maior que função principal")
    return {"year":year,"education":{v:found.get(("education",v)) for v in COLUMNS.values()},
            "subfunctions":{sub:{v:found.get((sub,v)) for v in COLUMNS.values()} for sub in ("earlyChildhood","specialEducation")}}

def main():
    prev_path=DATA/"finance.json"
    try: prev=json.loads(prev_path.read_text(encoding="utf8"))
    except FileNotFoundError: prev={"schemaVersion":1,"series":[]}
    by_year={int(a["year"]):a for a in prev.get("series",[])}
    failures=[]
    years=[2025,2024,2023,2022,2021,2020,2019]
    for year in years:
        try:
            val=parse(year,get_data(year))
            by_year[year]=val
            print(f"DCA {year}: Empenhadas R$ {val['education']['committed']:,.2f}",flush=True)
        except Exception as exc:
            failures.append(f"{year}: {exc}")
            print("::warning::"+failures[-1],flush=True)
        time.sleep(1.1)  # SICONFI oficial limita 1 requisição por segundo
    if 2025 not in by_year:raise ValueError("Ano 2025 ausente. Nenhum dado novo será publicado.")
    out={"schemaVersion":1,"updatedAt":datetime.now(timezone.utc).isoformat(),
         "source":ENDPOINT,"annex":ANNEX,"municipalityCode":CITY,
         "unit":"BRL nominal","definition":"DCA Anexo I-E, função 12, cod_conta=TotalDespesas. Empenhada, liquidada e paga são etapas alternativas, não aditivas.",
         "series":[by_year[y] for y in sorted(by_year)],"failures":failures,
         "programs":[],"programStatus":"pending"}
    DATA.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf8",dir=DATA,delete=False) as f:
        json.dump(out,f,ensure_ascii=False,indent=2)
        name=f.name
    os.replace(name,prev_path)
    summary_path=DATA/"summary.json"
    summary=json.loads(summary_path.read_text(encoding="utf8"))
    summary["sourceInfo"]["siconfi"]={"status":"ok","reference":"2019–2025 (anos com cobertura validada)",
       "url":ENDPOINT,"updatedAt":out["updatedAt"],
       "note":"Despesas por função orçamentária (educação), DCA anual; não são repasses do FNDE ou despesas por escola."}
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf8",dir=DATA,delete=False) as f:
        json.dump(summary,f,ensure_ascii=False,indent=2);name=f.name
    os.replace(name,summary_path)
    print("SICONFI anos publicados:",list(sorted(by_year)), "falhas:",failures)

if __name__=="__main__":main()
