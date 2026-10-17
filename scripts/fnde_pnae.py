#!/usr/bin/env python3
"""Extrai previsões de repasse PNAE 2024 do XLSX primário do FNDE.

O arquivo é *Previsão Repasse Financeiro*, não execução/pagamento. Unidade:
Prefeitura Municipal de Canoas/RS; nunca atribuir a escolas.
"""
from __future__ import annotations
import hashlib, io, json, os, re, tempfile, time, urllib.request, zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"public"/"data"
URL="https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/pnae/consultas/repasses-financeiros-por-entidade-executora/DadosFinanceirosdoPNAE_RedesEstadual_Distrital_Municipal_PorEntidadeExecutora_2024.xlsx/@@download/file"
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
ACTION={
 "PNACN":"Creche",
 "PNAEE":"Atendimento Educacional Especializado (AEE)",
 "PNAPN":"Pré-escola",
 "PNAFN":"Ensino fundamental",
 "PNAEN":"Educação de Jovens e Adultos (EJA)",
 "PNAMN":"Ensino médio",
 "PNAIN":"Indígena",
 "PNAQN":"Quilombola",
 "PNAMI":"Ensino médio em tempo integral",
}
def download()->bytes:
 error=None
 for trial in range(3):
  try:
   req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; WebGIS-Educacao-Canoas/0.4)"})
   with urllib.request.urlopen(req,timeout=50) as resp:
    if resp.status!=200:raise RuntimeError(f"HTTP {resp.status}")
    payload=resp.read(8_000_001)
   if len(payload)>8_000_000 or len(payload)<5000 or payload[:2]!=b"PK":
    raise ValueError("Arquivo FNDE ausente, grande demais ou não é XLSX")
   return payload
  except Exception as exc:
   error=exc
   if trial<2:time.sleep(3*(trial+1))
 raise RuntimeError(f"PNAE 2024 indisponível: {error}")
def decimal_br(value:str)->Decimal:
 try:
  n=Decimal(value.replace("R$","").replace(".","").replace(",",".").strip())
 except (InvalidOperation,AttributeError):
  raise ValueError("Montante PNAE inválido: "+str(value))
 if not n.is_finite() or n<0:raise ValueError("Montante negativo/não finito")
 return n
def sheet_rows(blob:bytes):
 with zipfile.ZipFile(io.BytesIO(blob)) as z:
  if "xl/worksheets/sheet1.xml" not in z.namelist():raise ValueError("FNDE: primeira planilha ausente")
  strings=[]
  if "xl/sharedStrings.xml" in z.namelist():
   root=ET.fromstring(z.read("xl/sharedStrings.xml"))
   strings=["".join(x.text or "" for x in si.findall(".//m:t",NS)) for si in root.findall("m:si",NS)]
  with z.open("xl/worksheets/sheet1.xml") as handle:
   for _,node in ET.iterparse(handle,events=["end"]):
    if node.tag.endswith("}row"):
     record={}
     for c in node.findall("m:c",NS):
      ref=c.attrib.get("r","")
      m=re.match(r"([A-Z]+)",ref)
      if not m or m.group(1) not in ("A","B","C","D","E"):continue
      v=c.find("m:v",NS)
      inline=c.find("m:is",NS)
      text=v.text if v is not None else ""
      if c.attrib.get("t")=="s" and text:text=strings[int(text)]
      if inline is not None:text="".join(i.text or "" for i in inline.findall(".//m:t",NS))
      record[m.group(1)]=(text or "").strip()
     yield record
     node.clear()
def parse(blob:bytes):
 rows=sheet_rows(blob)
 header_found=False
 found=[]
 for row in rows:
  if not header_found:
   if [row.get(c) for c in ("A","B","C","D","E")]==["UF","ENTIDADE_RESP","ACAO","QTDE_ALUNO","VALOR_PREVISTO"]:
    header_found=True
   continue
  if row.get("A")=="RS" and "CANOAS" in row.get("B","").upper():
   if "PREF" not in row["B"].upper() or not re.search(r"\bCANOAS\b",row["B"].upper()):
    raise ValueError("FNDE: entidade com nome de Canoas fora da prefeitura municipal: "+row["B"])
   code=row.get("C","")
   if code not in ACTION:raise ValueError("FNDE: ação desconhecida para Canoas: "+code)
   if not row.get("D","").replace(".","").isdigit():raise ValueError("Quantidade PNAE inválida: "+str(row))
   students=int(row["D"].replace(".",""))
   money=decimal_br(row.get("E",""))
   found.append({"code":code,"name":ACTION[code],"studentsForAction":students,
                 "amountPlannedBRL":float(money),"entity":row["B"]})
 if not header_found:raise ValueError("FNDE: cabeçalho esperado não encontrado")
 if not 2<=len(found)<=14:raise ValueError("FNDE: quantidade de ações Canoas suspeita: "+str(len(found)))
 if len({a["code"] for a in found})!=len(found):raise ValueError("FNDE: ação duplicada para Canoas")
 total=sum((Decimal(str(a["amountPlannedBRL"])) for a in found),Decimal("0"))
 if not Decimal("100000")<total<Decimal("70000000"):raise ValueError("FNDE: total previsto fora da faixa plausível")
 return sorted(found,key=lambda a:a["code"]),round(float(total),2)
def main():
 blob=download()
 lines,total=parse(blob)
 now=datetime.now(timezone.utc).isoformat()
 obj={"schemaVersion":1,"municipalityCode":4304606,"year":2024,
      "source":URL,"sourceHashSHA256":hashlib.sha256(blob).hexdigest(),
      "updatedAt":now,"scope":"PREF MUN DE CANOAS · RS",
      "fundingStatus":"planned","program":"PNAE","currency":"BRL",
      "definition":"PREVISÃO de repasse financeiro PNAE em 2024, por ação/modalidade e entidade executora. Não é total de valores efetivamente transferidos.",
      "totalPlannedBRL":total,"actions":lines,
      "caveat":"QTDE_ALUNO é quantidade por ação. O mesmo estudante pode participar de ações diferentes. NÃO somar como pessoas únicas. Valores não estão vinculados a escolas."}
 DATA.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile("w",encoding="utf8",dir=DATA,delete=False) as f:
  json.dump(obj,f,ensure_ascii=False,indent=2);path=f.name
 os.replace(path,DATA/"pnae.json")
 print(f"FNDE PNAE {obj['year']} Canoas: ações={len(lines)}, total previsto R$ {total:,.2f} SHA256={obj['sourceHashSHA256']}",flush=True)
 for row in lines:print("ACAO",row,flush=True)
if __name__=="__main__":main()
