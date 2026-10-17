import urllib.request,urllib.parse
from bs4 import BeautifulSoup
BASE="https://www.fnde.gov.br/pddeinfo/pddeinfo/escola/consultar"
for code in ["43170102","43037836"]:
 params=urllib.parse.urlencode(dict(ano=2025,co_escola=code,consultar="Consultar"))
 with urllib.request.urlopen(urllib.request.Request(BASE+"?"+params,headers={"User-Agent":"Mozilla/5.0"}),timeout=30) as r:
  body=r.read().decode("utf-8","replace")
 soup=BeautifulSoup(body,"html.parser")
 print("SCHOOL",code,"TOTAL_HTML",len(body))
 for idx,table in enumerate(soup.select("table.govbr-table")):
  heads=[x.get_text(" ",strip=True) for x in table.select("th")][:22]
  rows=[]
  for tr in table.find_all("tr"):
   cells=[x.get_text(" ",strip=True) for x in tr.find_all(["td","th"],recursive=False)]
   if cells:rows.append(cells)
  print("TABLE",idx,"HEADS",heads,"ROWCOUNT",len(rows))
  for x in (rows[:3]+rows[-4:]):
   print("ROW",str(x)[:750])
 for name in ("govbr-school-card","govbr-school-link-title"):
  print("SELECT",name,len(soup.select("."+name)))
