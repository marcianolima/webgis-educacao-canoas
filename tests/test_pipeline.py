import csv
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "scripts"))
import inep_censo as inep

class TransformTests(unittest.TestCase):
    def example(self, count=100001):
        # Usa gerador sintético apenas em testes; nenhuma amostra é publicada.
        row = {"CO_ENTIDADE":"12345678","CO_MUNICIPIO":"430460","NO_ENTIDADE":"ESCOLA TESTE",
               "TP_DEPENDENCIA":"3","TP_SITUACAO_FUNCIONAMENTO":"1","QT_MAT_BAS":"200",
               "NU_LATITUDE":"-29,91","NU_LONGITUDE":"-51,16",
               "IN_INTERNET":"1","QT_MAT_INF":"50"}
        lines = [row]+[
            {**row,"CO_ENTIDADE":str(10000000+i),"CO_MUNICIPIO":"3550308"}
            for i in range(count-1)
        ]
        # O limite de cobertura deve ser exercitado no teste com poucas linhas.
        return lines

    def test_conversion_and_coordinates(self):
        row={"CO_ENTIDADE":"12345678","TP_DEPENDENCIA":"3",
             "TP_SITUACAO_FUNCIONAMENTO":"1","NO_ENTIDADE":"Unidade",
             "QT_MAT_BAS":"240","NU_LATITUDE":"-29,95",
             "NU_LONGITUDE":"-51,18","IN_INTERNET":"1"}
        d=inep.convert_row(row)
        self.assertEqual((d["inep"],d["network"]),("12345678","Municipal"))
        self.assertIsNone(d["enrollments"])  # matrículas vêm da Tabela_Matricula, não de Tabela_Escola
        self.assertEqual((d["latitude"],d["longitude"]),(-29.95,-51.18))
        self.assertTrue(d["infrastructure"]["Internet"])
        self.assertIsNone(d["infrastructure"]["Biblioteca"])

    def test_outside_coordinates_not_invented(self):
        row={"CO_ENTIDADE":"12345678","TP_DEPENDENCIA":"2",
             "TP_SITUACAO_FUNCIONAMENTO":"1","NO_ENTIDADE":"Escola",
             "NU_LATITUDE":"-22.9","NU_LONGITUDE":"-43.2"}
        d=inep.convert_row(row)
        self.assertIsNone(d["latitude"])
        self.assertIsNone(d["longitude"])

    def test_school_stage_totals_await_other_table(self):
        row={"CO_ENTIDADE":"12345678","TP_DEPENDENCIA":"3",
             "TP_SITUACAO_FUNCIONAMENTO":"1","NO_ENTIDADE":"Escola",
             "QT_MAT_BAS":"9999","QT_MAT_INF":"9999"}
        school=inep.convert_row(row)
        self.assertIsNone(school["enrollments"])
        self.assertTrue(all(v is None for v in school["stages"].values()))

    def test_municipal_code_both_formats(self):
        self.assertEqual(inep.CANOAS,{"430460","4304606"})

    def test_null_is_not_zero(self):
        self.assertIsNone(inep.integer(None))
        self.assertEqual(inep.integer("0"),0)
        self.assertIsNone(inep.flag(None))
        self.assertFalse(inep.flag("0"))

    def test_missing_required_columns_rejected(self):
        reader=csv.DictReader(io.StringIO("CO_ENTIDADE;NO_ENTIDADE\n12345678;Escola\n"),delimiter=";")
        with self.assertRaisesRegex(ValueError,"obrigatórias"):
            inep.transform(reader)

class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d=ROOT/"public"/"data"
        cls.s=json.loads((d/"summary.json").read_text(encoding="utf8"))
        cls.c=json.loads((d/"schools.json").read_text(encoding="utf8"))
        cls.g=json.loads((d/"schools.geojson").read_text(encoding="utf8"))

    def test_municipality(self):
        self.assertEqual(self.s["municipality"]["ibge"],"4304606")
        self.assertEqual(self.s["municipality"]["populationCensusYear"],2022)

    def test_school_catalog_consistent(self):
        schools=self.c["schools"]
        codes=[x["inep"] for x in schools]
        self.assertEqual(len(codes),len(set(codes)))
        for school in schools:
            self.assertRegex(school["inep"],r"^\d{8}$")
            self.assertEqual(school["city"],"Canoas")
            self.assertIn(school["network"],inep.NETWORKS.values())
        count=self.s["education"]["totalSchools"]
        if count is not None:
            self.assertEqual(count,len(schools))
            self.assertGreater(count,30)
            self.assertEqual(count,sum(self.s["education"]["schoolsByNetwork"].values()))

    def test_geojson_coords_and_catalog_join(self):
        ids={s["inep"] for s in self.c["schools"]}
        self.assertEqual(self.g["type"],"FeatureCollection")
        for f in self.g["features"]:
            self.assertIn(f["properties"]["inep"],ids)
            lon,lat=f["geometry"]["coordinates"]
            self.assertTrue(-51.42<=lon<=-50.92)
            self.assertTrue(-30.12<=lat<=-29.72)

    def test_no_direct_personal_identifiers(self):
        serialized=json.dumps({"schools":self.c["schools"],"features":self.g["features"]}).lower()
        for forbidden in ['"cpf"','"nis"','"nome_aluno"','"nome_docente"','"data_nascimento"']:
            self.assertNotIn(forbidden,serialized)

    def test_enrollment_reconciliation(self):
        e=self.s["education"]
        if e["totalEnrollments"] is not None:
            active=[x for x in self.c["schools"] if x["status"]=="Em atividade"]
            self.assertTrue(active)
            self.assertTrue(all(x["enrollments"] is not None for x in active))
            self.assertEqual(e["totalEnrollments"],sum(x["enrollments"] for x in active))
            self.assertEqual(e["totalEnrollments"],sum(e["enrollmentsByNetwork"].values()))

if __name__=="__main__":
    unittest.main()

class SeducGeometryTests(unittest.TestCase):
    def test_2023_spatial_catalog_never_claims_school_universe(self):
        from seduc_geo import combine
        a=[{"inep":"12345678","name":"Escola Oficial","network":"Municipal",
            "latitude":-29.95,"longitude":-51.18,"address":"Rua Pública"}]
        cat, diag=combine({"year":None,"schools":[]},a)
        self.assertEqual(cat["year"],2023)
        self.assertEqual(len(cat["schools"]),1)
        self.assertIsNone(cat["schools"][0]["enrollments"])
        self.assertEqual(diag["mode"],"2023-map-only")
    def test_join_by_inep_without_overwriting_new_coordinates(self):
        from seduc_geo import combine
        data={"year":2025,"schools":[{"inep":"12345678","latitude":-29.92,"longitude":-51.16},
                                      {"inep":"22222222","latitude":None,"longitude":None}]}
        geo=[{"inep":"12345678","latitude":-29.95,"longitude":-51.18},
             {"inep":"22222222","latitude":-29.96,"longitude":-51.19}]
        cat,diag=combine(data,geo)
        self.assertEqual(cat["schools"][0]["latitude"],-29.92)
        self.assertEqual(cat["schools"][1]["latitude"],-29.96)
        self.assertEqual(diag["supplementedCoordinates"],1)


class SEDUCExtendedMetadataTests(unittest.TestCase):
    def test_seduc_offers_and_no_false_enrollment_year(self):
        cat=json.loads((ROOT/"public"/"data"/"schools.json").read_text(encoding="utf8"))
        if cat["year"]!=2023:return
        rows=cat["schools"]
        self.assertGreater(len([s for s in rows if (s.get("seducDetails") or {}).get("educationOffer")]),30)
        for s in rows:
            d=s.get("seducDetails") or {}
            if d.get("stateReportedEnrollment") is not None:
                self.assertEqual(s["network"],"Estadual")
                self.assertIsNone(d.get("reportedCountsYear"))
                self.assertIsNone(s["enrollments"])
