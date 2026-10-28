"""Falha de rede FNDE deve preservar snapshot, falha de integridade não."""
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import fnde_transfers

DATA = Path(__file__).resolve().parents[1] / "public" / "data"

class FndeResilienceTests(unittest.TestCase):
    def test_http_404_keeps_valid_snapshot_byte_for_byte(self):
        snap = DATA / "fnde_actuals.json"
        old = snap.read_bytes()
        with patch.object(fnde_transfers, "fetch", side_effect=RuntimeError("FNDE 82: ['HTTP Error 404: Not Found']")):
            fnde_transfers.main()
        self.assertEqual(snap.read_bytes(), old)
        self.assertEqual(json.loads(snap.read_text(encoding="utf-8"))["pnae"]["sourceProductId"],82)

    def test_schema_error_is_not_masked_by_cached_snapshot(self):
        with patch.object(fnde_transfers,"fetch",side_effect=RuntimeError("FNDE 82: tamanho/magic incompatíveis")):
            with self.assertRaisesRegex(RuntimeError, "magic incompatíveis"):
                fnde_transfers.main()

if __name__ == "__main__":
    unittest.main()
