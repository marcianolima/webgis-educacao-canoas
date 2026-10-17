#!/usr/bin/env python3
"""Inspect authoritative FNDE PNAE annual workbook format; no publication."""
import json,urllib.request,urllib.parse,io,zipfile,re,xml.etree.ElementTree as E,traceback
from html.parser import HTMLParser
URLS={
"pnae2024":"https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/pnae/consultas/repasses-financeiros-por-entidade-executora/DadosFinanceirosdoPNAE_RedesEstadual_Distrital_Municipal_PorEntidadeExecutora_2024.xlsx/@@download/file",
"pnae2023":"https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/pnae/consultas/repasses-financeiros-por-entidade-executora/DadosFinanceirosdoPNAE_RedesEstadual_Distrital_Municipal_PorEntidadeExecutora_2023.xlsx/@@download/file",
"antonieta":"https://www.fnde.gov.br/plataforma-antonieta-de-barros/dados/produtos-de-dados/visualizar/82",
}
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
def inspect_excel(blob):
    z=zipfile.ZipFile(io.BytesIO(blob))
    names=z.namelist()
    print("ZIP_FILES",names[:12],flush=True)
    sheets=[x for x in names if re.fullmatch(r"xl/worksheets/sheet\d+\.xml",x)]
    shared=[]
    if "xl/sharedStrings.xml" in names:
        root=E.fromstring(z.read("xl/sharedStrings.xml"))
        shared=["".join(t.text or "" for t in x.findall(".//m:t",NS)) for x in root.findall("m:si",NS)]
    print("SHEETS",sheets,"SHARED",len(shared),flush=True)
    for path in sheets[:12]:
        first=[]
        with z.open(path) as f:
            for event,node in E.iterparse(f,events=["end"]):
                if node.tag.endswith("}row"):
                    cells=[]
                    for c in node.findall("m:c",NS):
                        v=c.find("m:v",NS)
                        inline=c.find("m:is",NS)
                        val=(v.text if v is not None else None)
                        if c.attrib.get("t")=="s" and val is not None:val=shared[int(val)]
                        if inline is not None:val="".join(n.text or "" for n in inline.findall(".//m:t",NS))
                        if val is not None:cells.append((c.attrib.get("r"),str(val)[:100]))
                    if cells:first.append(cells[:22])
                    node.clear()
                    if len(first)>=12:break
        print("SHEET_SAMPLE",path,first,flush=True)
for key,url in URLS.items():
 print("\nTARGET",key,url,flush=True)
 try:
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; WebGIS-Educacao-Canoas/1.0)"})
    with urllib.request.urlopen(req,timeout=65) as resp:
        print("STATUS",resp.status,"TYPE",resp.headers.get("Content-Type"),"LENGTH",resp.headers.get("Content-Length"),"FINAL",resp.url,flush=True)
        blob=resp.read(37*1024*1024+1)
    print("BYTES",len(blob),flush=True)
    if key.startswith("pnae") and blob[:2]==b"PK" and len(blob)<37*1024*1024: inspect_excel(blob)
    elif key=="antonieta":
        html=blob.decode("utf-8",errors="replace")
        hits=re.findall(r'(?:https?[^"\s<>]+|/[^"\s<>]+)',html)
        print("ANTONIETA_LINKS",[(x[:220]) for x in hits if any(k in x.lower() for k in ("artefato","download","export","api/","product","blob","files/"))][:25],flush=True)
 except Exception as ex:
    print("ERROR",key,str(ex),flush=True)
