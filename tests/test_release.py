"""Validações transversais da versão pública 1.0: sem inferências territoriais."""
import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "public" / "data"

def read(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))

class ReleaseIntegrityTests(unittest.TestCase):
    def test_catalogue_and_2025_coverages(self):
        catalogue = read("schools.json")
        summary = read("summary.json")
        schools = catalogue["schools"]
        self.assertEqual(catalogue["year"], 2025)
        self.assertEqual(len(schools), 204)
        self.assertEqual(sum(s["status"] == "Em atividade" for s in schools), 196)
        self.assertEqual(summary["education"]["totalSchools"], 196)
        self.assertEqual(sum(s["latitude"] is not None and s["longitude"] is not None for s in schools), 169)
        self.assertEqual(len({s["inep"] for s in schools}), len(schools))
        self.assertTrue(all(s["coordinateSource"] is not None for s in schools if s["latitude"] is not None))
        self.assertEqual(sum(summary["education"]["schoolsByNetwork"].values()), 196)
        self.assertEqual(sum(summary["education"]["enrollmentsByNetwork"].values()), 68490)
    def test_primary_ideb_covers_only_published_schools(self):
        ideb = read("ideb_schools.json")
        self.assertEqual(ideb["municipalityCode"], "4304606")
        self.assertEqual(ideb["year"], 2025)
        stages = ideb["stages"]
        for stage in ("fundamentalInitial", "fundamentalFinal", "highSchool"):
            records = stages[stage]["records"]
            self.assertGreater(len(records), 0)
            for code, row in records.items():
                self.assertRegex(code, r"^[0-9]{8}$")
                self.assertEqual(row["inep"], code)
                self.assertEqual(row["year"], 2025)
    def test_auditable_transfers_are_not_ascribed_to_schools(self):
        raw = read("fnde_actuals.json")
        self.assertEqual(raw["municipalityCode"], "4304606")
        self.assertEqual(raw["pnae"]["sourceProductId"], 82)
        self.assertEqual(raw["pnate"]["sourceProductId"], 56)
        self.assertIn("a pagar", raw["pnate"]["measure"])
        self.assertNotIn("byInep", raw["pnae"])
        self.assertNotIn("byInep", raw["pnate"])
        self.assertEqual(read("summary.json")["sourceInfo"]["fnde"]["status"], "ok")

if __name__ == "__main__": unittest.main()
