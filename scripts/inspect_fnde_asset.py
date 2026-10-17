#!/usr/bin/env python3
"""Diagnóstico URL API pública FNDE frontend (read-only)."""
import re,urllib.request
url="https://www.fnde.gov.br/plataforma-antonieta-de-barros/assets/index-Dy0c8hD4.js"
req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
with urllib.request.urlopen(req,timeout=38) as r:raw=r.read(13_000_001)
text=raw.decode("utf-8","replace")
print("JS_SIZE",len(raw),flush=True)
for word in ("AUTO_STORING","exportArtifact","downloadArtifact","exportarArtefato","artefato","artifact","presigned","signed-url","download","/api/","/v1/","BASE_URL","axios.create","storage"):
 matches=list(re.finditer(re.escape(word),text,re.I))
 print("TERM",word,"n",len(matches),flush=True)
 for m in matches[:4]:
  start=max(0,m.start()-200)
  print("SNIP",text[start:m.end()+240].replace("\n"," ")[:450],flush=True)
print("ENDPOINTS",list(dict.fromkeys(re.findall(r'["\\\']((?:https?://[^"\\\']+|/[^"\\\']+)(?:artifact|artefato|download|export|api)[^"\\\']*)',text,re.I)))[:50],flush=True)
