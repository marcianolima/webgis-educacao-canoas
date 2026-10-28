#!/usr/bin/env python3
"""FNDE: PNAE (valores reportados como repassados) e PNATE (valores a pagar).

Fonte oficial Plataforma Antonieta de Barros. O CNPJ identifica exclusivamente
ente público; nenhum dado pessoal nem arquivo bruto é publicado.
"""
from __future__ import annotations
import csv,gzip,hashlib,io,json,os,tempfile,time,urllib.request
from decimal import Decimal,InvalidOperation
from pathlib import Path
from datetime import datetime,timezone

BASE="https://www.fnde.gov.br/plataforma-antonieta-de-barros-api/products/data-products"
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"public"/"data"
CNPJ="88577416000118"
MAX_BYTES=6_000_000

def fetch(product:int)->tuple[bytes,dict]:
    errors=[]
    for attempt in range(3):
        try:
            req=urllib.request.Request(f"{BASE}/{product}/artifact-metadata",
              headers={"User-Agent":"WebGIS-Educacao-Canoas/0.5","Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=35) as r:meta=json.loads(r.read(8192))
            size=int(meta["size"])
            if not 1000<size<MAX_BYTES:raise ValueError(f"FNDE {product}: arquivo acima do limite {size}")
            req=urllib.request.Request(f"{BASE}/{product}/artifact",
              headers={"User-Agent":"WebGIS-Educacao-Canoas/0.5"})
            with urllib.request.urlopen(req,timeout=55) as r:raw=r.read(MAX_BYTES+1)
            if len(raw)!=size or not raw.startswith(b"\x1f\x8b"):
                raise ValueError(f"FNDE {product}: comprimento/magic incompatíveis: {len(raw)}/{size}")
            return raw,meta
        except Exception as ex:
            errors.append(str(ex))
            if attempt<2:time.sleep(3*(attempt+1))
    raise RuntimeError(f"FNDE {product}: {errors}")

def dec(text:str,allow_null:bool=False)->Decimal|None:
    text=str(text or "").strip()
    if not text and allow_null:return None
    try:n=Decimal(text.replace(",","."))
    except InvalidOperation:raise ValueError("Valor monetário inválido "+repr(text))
    if not n.is_finite() or n<0:raise ValueError("Valor negativo/infinito")
    return n

def read_rows(data:bytes):
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as f:
        with io.TextIOWrapper(f,encoding="utf-8-sig",errors="replace",newline="") as text:
            reader=csv.DictReader(text,delimiter=";")
            if not reader.fieldnames:raise ValueError("Arquivo sem cabeçalho")
            for i,row in enumerate(reader):
                if i>=1_000_000:raise ValueError("Limite de linhas nacional excedido")
                yield row

def pnae(raw:bytes):
    found={}
    national=0
    for row in read_rows(raw):
        national+=1
        if row.get("UF")!="RS" or row.get("Municipio")!="CANOAS" or row.get("CNPJ_Responsavel")!=CNPJ:continue
        if row.get("Entidade_Responsavel")!="PREF MUN DE CANOAS":
            raise ValueError("PNAE entidade inconsistência")
        year=int(row["Ano_Exercicio"])
        if not 2009<=year<=2026:raise ValueError("Exercício PNAE anômalo")
        if year in found:raise ValueError(f"PNAE: duplicado Canoas {year}")
        value=dec(row.get("Valor_Repasse"),allow_null=True)
        number=int(row["Quantidade_Alunos"])
        schools=int(row["Quantidade_Escolas"])
        if not 5000<=number<=150000 or not 20<=schools<=500:raise ValueError("PNAE: quantidades suspeitas")
        found[year]={"year":year,"studentsConsidered":number,"schoolsServed":schools,
                     "reportedTransferredBRL":float(value) if value is not None else None}
    if national<10_000 or len(found)<15 or 2025 not in found:
        raise ValueError(f"PNAE insuficiente: {national} registros nacionais / {len(found)} anos Canoas")
    if abs(found[2025]["reportedTransferredBRL"]-4439438)>1:
        raise ValueError("PNAE 2025 diverge da reconciliação inicial")
    if abs(found[2024]["reportedTransferredBRL"]-5895260.80)>1:
        raise ValueError("PNAE 2024 diverge da planilha de previsão 2024; investigar")
    return [found[y] for y in sorted(found)],national

def pnate(raw:bytes):
    found=[]
    for row in read_rows(raw):
        if row.get("sigla_uf")=="RS" and row.get("cod_ibge")=="4304606":
            if row.get("cnpj")!=CNPJ or row.get("entidade_executora")!="PREF MUN DE CANOAS":
                raise ValueError("PNATE: ente inconsistente")
            found.append(row)
    if len(found)!=1:raise ValueError(f"PNATE: era esperado 1 registro municipal, encontrado {len(found)}")
    r=found[0]
    out={}
    for stage,raw_key in [("earlyChildhood","vl_pagar_ed_infantil"),("elementary","vl_pagar_ens_fundamental"),("highSchool","vl_pagar_ens_medio")]:
        val=dec(r[raw_key])
        out[stage]=float(val)
    return {"reportedAt":r.get("data_arquivo"),"perCapitaBRL":float(dec(r["valor_per_capita"])),
       "delegatedStateNetwork":r.get("aut_repasse_delegacao_rede"),
       "toPayBRL":out,"totalToPayBRL":float(sum(Decimal(str(v)) for v in out.values()))}

def main():
    try:
        pbytes,pmeta=fetch(82)
        nbytes,nmeta=fetch(56)
    except RuntimeError as exc:
        # Não apagar dados conciliados por falha de rede do fornecedor.
        # Snapshot ausente, danificado ou divergente: falhar explicitamente.
        target=DATA/"fnde_actuals.json"
        if not target.is_file():raise
        old=json.loads(target.read_text(encoding="utf-8"))
        series=old.get("pnae",{}).get("series",[])
        valid=(old.get("municipalityCode")=="4304606"
          and old.get("pnae",{}).get("sourceProductId")==82
          and old.get("pnate",{}).get("sourceProductId")==56
          and len(series)>=15
          and any(x.get("year")==2025 and x.get("reportedTransferredBRL")==4439438.0 for x in series)
          and old.get("pnate",{}).get("totalToPayBRL") is not None)
        if not valid:raise RuntimeError("Fonte FNDE indisponível e snapshot existente inválido") from exc
        print(f"::warning::FNDE indisponível ({exc}). Snapshot validado preservado sem atualizar a data de coleta: {old.get('updatedAt','sem data')}",flush=True)
        return
    series,national=pnae(pbytes)
    pn=pnate(nbytes)
    now=datetime.now(timezone.utc).isoformat()
    result={"schemaVersion":1,"municipalityCode":"4304606","updatedAt":now,
      "pnae":{"sourceProductId":82,"source":BASE+"/82/artifact","sourcePage":"https://www.fnde.gov.br/plataforma-antonieta-de-barros/dados/produtos-de-dados/visualizar/82",
       "reference":"2009–2026; 2026 sem valor divulgado no arquivo", "sourceSHA256":hashlib.sha256(pbytes).hexdigest(),
       "sourceUpdatedAt":pmeta.get("lastUpdated"),
       "measure":"Valor_Repasse (campo oficial), agregado por ente executor/ano. Não é repasse por escola.",
       "series":series,"nationalRowsRead":national},
      "pnate":{"sourceProductId":56,"source":BASE+"/56/artifact",
        "sourcePage":"https://www.fnde.gov.br/plataforma-antonieta-de-barros/dados/produtos-de-dados/visualizar/56",
        "sourceSHA256":hashlib.sha256(nbytes).hexdigest(),
        "sourceUpdatedAt":nmeta.get("lastUpdated"),
        "measure":"vl_pagar_* (valor a pagar). Não equivale a pagamento efetivo; competência do arquivo não presumida.",
        **pn}}
    DATA.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=DATA,delete=False) as tmp:
        json.dump(result,tmp,ensure_ascii=False,indent=2);name=tmp.name
    os.replace(name,DATA/"fnde_actuals.json")
    print("FNDE PNAE",len(series),"anos. 2025:",next(s for s in series if s["year"]==2025),flush=True)
    print("FNDE PNATE",pn,flush=True)
if __name__=="__main__":main()
