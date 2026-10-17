import json
import unittest
from pathlib import Path

DATA=Path(__file__).resolve().parents[1]/"public"/"data"
class AdditionalDataTests(unittest.TestCase):
 def test_quality_scope_years(self):
  q=json.loads((DATA/"quality.json").read_text())
  self.assertEqual(q["municipality"],"4304606")
  series=q["ideb"]["series"]
  years=[r["year"] for r in series]
  self.assertEqual(years,sorted(set(years)))
  self.assertEqual(years[-1],2025)
  self.assertEqual(q["status"],"secondary_corroborated")
  for row in series:
   for metric in ("initialMunicipal","finalMunicipal","highState"):
    value=row[metric]
    if value is not None:
     self.assertGreaterEqual(value,0)
     self.assertLessEqual(value,10)
  self.assertEqual(series[-1]["initialMunicipal"],5.3)
  self.assertEqual(series[-1]["finalMunicipal"],4.6)
 def test_quality_no_school_imputation(self):
  q=json.loads((DATA/"quality.json").read_text())
  self.assertEqual(q["schoolIndicators"],[])
  self.assertEqual(q["saeb"]["status"],"secondary_single_source")
 def test_siconfi_annual_no_double_count(self):
  f=json.loads((DATA/"finance.json").read_text())
  self.assertEqual(f["municipalityCode"],4304606)
  self.assertEqual(f["annex"],"DCA-Anexo I-E")
  years=[r["year"] for r in f["series"]]
  self.assertEqual(years,sorted(set(years)))
  self.assertIn(2025,years)
  for row in f["series"]:
   e=row["education"]
   self.assertGreater(e["committed"],0)
   for sub in row["subfunctions"].values():
    for key in ("committed","liquidated","paid"):
     v=sub.get(key)
     if v is not None:
      self.assertLessEqual(v,e[key])
  latest=next(row for row in f["series"] if row["year"]==2025)
  self.assertAlmostEqual(latest["education"]["committed"],525098080.19,places=2)
  self.assertAlmostEqual(latest["education"]["liquidated"],478477062.27,places=2)
  self.assertAlmostEqual(latest["education"]["paid"],395913248.00,places=2)
 def test_missing_not_zero(self):
  f=json.loads((DATA/"finance.json").read_text())
  self.assertTrue(any(s["subfunctions"]["specialEducation"]["committed"] is None for s in f["series"]))

class PNAETests(unittest.TestCase):
 def test_2024_planned_only(self):
  d=json.loads((DATA/"pnae.json").read_text(encoding="utf8"))
  self.assertEqual(d["year"],2024)
  self.assertEqual(d["municipalityCode"],4304606)
  self.assertEqual(d["fundingStatus"],"planned")
  self.assertEqual(len(d["actions"]),5)
  self.assertAlmostEqual(d["totalPlannedBRL"],5895260.80,places=2)
  self.assertAlmostEqual(sum(x["amountPlannedBRL"] for x in d["actions"]),d["totalPlannedBRL"],places=2)
  self.assertEqual(len({x["code"] for x in d["actions"]}),len(d["actions"]))

class DemographicIBGETests(unittest.TestCase):
 def test_age_bands_population_and_nonoverlap(self):
  d=json.loads((DATA/"ibge_age.json").read_text(encoding="utf8"))
  self.assertEqual(d["municipalityCode"],"4304606")
  self.assertEqual(d["year"],2022)
  self.assertEqual(d["totalPopulation"],347657)
  ages=d["ageSingles"]
  self.assertEqual(len(ages),25)
  self.assertEqual(sum(ages[str(a)] for a in range(18)),d["ageGroups"]["0–17 anos"])
  self.assertEqual(sum(ages[str(a)] for a in range(4)),d["ageGroups"]["0–3 anos"])
  self.assertEqual(sum(ages[str(a)] for a in (4,5)),d["ageGroups"]["4–5 anos"])
  self.assertEqual(sum(ages[str(a)] for a in range(6,15)),d["ageGroups"]["6–14 anos"])
  self.assertEqual(sum(ages[str(a)] for a in range(15,18)),d["ageGroups"]["15–17 anos"])
  self.assertGreater(d["totalPopulation"],sum(d["ageGroups"][k] for k in ("0–3 anos","4–5 anos","6–14 anos","15–17 anos","18–24 anos")))

class FNDEActualTransferTests(unittest.TestCase):
 def test_pnae_series_and_pnate_semantics(self):
  d=json.loads((DATA/"fnde_actuals.json").read_text(encoding="utf8"))
  self.assertEqual(d["municipalityCode"],"4304606")
  s=d["pnae"]["series"]
  self.assertEqual(len({y["year"] for y in s}),len(s))
  self.assertGreaterEqual(len(s),16)
  x=next(y for y in s if y["year"]==2025)
  self.assertAlmostEqual(x["reportedTransferredBRL"],4439438.0,places=2)
  self.assertEqual(x["schoolsServed"],91)
  self.assertEqual(x["studentsConsidered"],35421)
  self.assertIn("vl_pagar",d["pnate"]["measure"])
  self.assertAlmostEqual(d["pnate"]["totalToPayBRL"],437.16,places=2)
  self.assertAlmostEqual(sum(d["pnate"]["toPayBRL"].values()),d["pnate"]["totalToPayBRL"],places=2)

class ReconciledSchoolDataTests(unittest.TestCase):
 def test_censo_2025(self):
  d=json.loads((DATA/"rs_censo_municipal.json").read_text())
  t={k:next(x for x in d["enrollments"][k] if x["year"]==2025) for k in ("Todas","Municipal","Estadual","Federal","Privada")}
  self.assertEqual((t["Todas"]["mat_total"],t["Todas"]["schools"]),(68490,196))
  self.assertEqual((t["Municipal"]["mat_total"],t["Municipal"]["schools"]),(30597,82))
  self.assertEqual(sum(t[k]["mat_total"] for k in ("Municipal","Estadual","Federal","Privada")),68490)
 def test_pdde_payments(self):
  d=json.loads((DATA/"pdde_schools.json").read_text())
  self.assertEqual(d["municipalityCode"],"4304606")
  self.assertEqual(d["year"],2025)
  self.assertGreaterEqual(d["schoolsWithPublishedPayments"],70)
  for inep,s in d["byInep"].items():
   self.assertRegex(inep,"^[0-9]{8}$")
   self.assertNotIn("cnpj",s)
   self.assertNotIn("account",s)
   if s["status"]=="ok":
    self.assertAlmostEqual(sum(p["paidBRL"] for p in s["payments"]),s["paidBRL"],places=2)
  self.assertAlmostEqual(sum(s["paidBRL"] for s in d["byInep"].values() if s["status"]=="ok"),d["totalPaidRespondedBRL"],places=2)
