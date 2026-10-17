#!/usr/bin/env python3
"""Extrai transferências pagas do PDDE Info por escola INEP (2025).

A fonte pública identifica escola e ano. Publica apenas agregados financeiros
e itens de programa/ação, NUNCA números de contas bancárias ou CNPJs.
"""
from __future__ import annotations
import concurrent.futures,datetime,decimal,json,os,re,tempfile,time,urllib.parse,urllib.request
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"public"/"data"
SOURCE="https://www.fnde.gov.br/pddeinfo/pddeinfo/escola/consultar"
YEAR=2025
def cash(value):
    val=str(value or "").strip()
    if val in ("","-"):return None
    try:amt=decimal.Decimal(val.replace(".","").replace(",","."))
    except decimal.InvalidOperation:raise ValueError("Moeda PDDE inválida: "+repr(value))
    if not amt.is_finite() or amt<0 or amt>decimal.Decimal("100000000"):raise ValueError("PDDE valor inválido")
    return amt
def parse(html,inep):
    soup=BeautifulSoup(html,"html.parser")
    if not soup.select(".govbr-school-link-title"):
        return {"inep":inep,"year":YEAR,"status":"no-official-result","paidBRL":None,"payments":[]}
    matches=[b for b in soup.select(".govbr-school-link-title") if inep in b.get_text(" ",strip=True)]
    if len(matches)!=1:raise ValueError(f"INEP {inep}: retorno de escola errada ou duplicada")
    tables=soup.select("table.govbr-table")
    general=[]
    payments=[]
    for table in tables:
        th=[x.get_text(" ",strip=True) for x in table.find_all("th")]
        # First table contains bank account balances -> prohibited, ignore entirely
        if "Valor Pago Total" not in th:continue
        index=th.index("Valor Pago Total")
        is_total="Filtro Geral" in th
        if is_total:
            for row in table.find_all("tr"):
                cells=[c.get_text(" ",strip=True) for c in row.find_all(["td","th"],recursive=False)]
                if cells and cells[0]=="TOTAL GERAL":
                    general.append(cash(cells[index]))
            continue
        if "Data do Pagamento" not in th:raise ValueError("PDDE falta coluna Data do Pagamento")
        dateidx=th.index("Data do Pagamento")
        for row in table.find_all("tr"):
            cells=[c.get_text(" ",strip=True) for c in row.find_all(["td","th"],recursive=False)]
            if not cells or cells[0] in ("Subtotal","Destinação") or len(cells)<=max(index,dateidx):
                continue
            amount=cash(cells[index])
            date=cells[dateidx]
            if amount is None or amount==0:continue
            try:dt=datetime.datetime.strptime(date,"%d/%m/%Y").date()
            except ValueError:raise ValueError(f"PDDE sem data de pagamento para valor positivo: {inep} {date}")
            if dt.year!=YEAR:raise ValueError(f"PDDE data de pagamento em ano incompatível: {dt}")
            payments.append({"program":cells[0][:180],"paidBRL":float(amount),"paymentDate":dt.isoformat()})
    if len(general)!=1:raise ValueError(f"PDDE {inep}: não é possível conferir TOTAL GERAL")
    official=general[0]
    if official is None:raise ValueError("PDDE TOTAL GERAL sem pagamento")
    paid=sum((decimal.Decimal(str(x["paidBRL"])) for x in payments),decimal.Decimal(0))
    if abs(paid-official)>decimal.Decimal(".05"):
        raise ValueError(f"PDDE {inep} total de linhas {paid} não confere total geral {official}")
    return {"inep":inep,"year":YEAR,"status":"ok","paidBRL":float(official),"paymentCount":len(payments),"payments":payments}
def retrieve(inep):
    params=urllib.parse.urlencode({"ano":YEAR,"co_escola":inep,"consultar":"Consultar"})
    url=SOURCE+"?"+params
    last=None
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"WebGIS-Educacao-Canoas/0.5 (consultas públicas municipais)","Accept":"text/html"})
            with urllib.request.urlopen(req,timeout=35) as resp:
                if resp.status!=200:raise RuntimeError(f"HTTP {resp.status}")
                blob=resp.read(450_001)
            if len(blob)>450000:raise ValueError("Página excede limite")
            return parse(blob.decode("utf-8",errors="replace"),inep)
        except Exception as e:
            last=e
            if attempt<2:time.sleep(2*(attempt+1))
    raise RuntimeError(f"PDDE {inep} falhou: {last}")
def main():
    cat=json.loads((DATA/"schools.json").read_text(encoding="utf-8"))
    schools=[s for s in cat["schools"] if s["network"]=="Municipal"]
    if not 40<=len(schools)<=140:raise ValueError(f"Catálogo municipal estranho {len(schools)}")
    ids=sorted(s["inep"] for s in schools)
    if len(ids)!=len(set(ids)):raise ValueError("INEPs repetidos")
    results={};errors={}
    # Baixa apenas escolas municipais presentes no cadastro cadastral SEDUC.
    # Pool pequeno para ser cortês com servidor público; cada request é individual.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures={executor.submit(retrieve,inep):inep for inep in ids}
        for fut in concurrent.futures.as_completed(futures):
            code=futures[fut]
            try:results[code]=fut.result()
            except Exception as e:
                errors[code]=str(e)[:240]
                print("::warning::",code,errors[code],flush=True)
    if sum(v['status']=='ok' for v in results.values())<max(3,len(ids)*0.1):
        raise ValueError('PDDE: todas/quase todas escolas sem resultado público: provável bloqueio de consultas ou erro de contrato; preservar snapshot anterior')
    if len(results)<len(ids)*0.8:
        raise ValueError(f"PDDE cobertura validada insuficiente: {len(results)}/{len(ids)}")
    paid=[v for v in results.values() if v["status"]=="ok"]
    total=sum(decimal.Decimal(str(v["paidBRL"])) for v in paid)
    out={"schemaVersion":1,"year":YEAR,"municipalityCode":"4304606","catalogYear":cat["year"],
        "scope":"Escolas da rede MUNICIPAL presentes no catálogo geográfico SEDUC/RS 2023",
        "source":SOURCE,"sourceType":"PDDE Info · consulta pública por código INEP e exercício",
        "updatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "schoolsChecked":len(ids),"schoolsResponded":len(results),"schoolsWithPublishedPayments":len(paid),
        "schoolsWithNoOfficialResult":sum(v["status"]=="no-official-result" for v in results.values()),
        "schoolsWithFetchErrors":len(errors),"totalPaidRespondedBRL":float(total),
        "coverageNote":"Somente escolas do catálogo municipal 2023. Total soma APENAS as respostas válidas; ausência/erro não são zeros. Não é total do PDDE de Canoas para todas as redes ou escolas ativas em 2025.",
        "byInep":dict(sorted(results.items())),"errors":errors}
    DATA.mkdir(exist_ok=True,parents=True)
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",dir=DATA,delete=False) as f:
        json.dump(out,f,ensure_ascii=False,indent=2);tmp=f.name
    os.replace(tmp,DATA/"pdde_schools.json")
    print(f"PDDE {YEAR}: respostas {len(results)}/{len(ids)}, escolas com pagamento {len(paid)}, total respondentes {total}",flush=True)
if __name__=="__main__":main()
