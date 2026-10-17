#!/usr/bin/env python3
"""Complementa coordenadas escolares a partir da IDE SEDUC/RS (base INEP 2023).

O serviço é fonte geográfica de 2023: nunca confunde essas posições com
matrículas, professores, IDEB ou outras medidas de 2025.
Na ausência de cadastro INEP validado, mantém catálogo preliminar de escolas
georreferenciadas de 2023 sem declarar universo municipal completo.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"
SERVICE = "https://iede.rs.gov.br/server/rest/services/SEDUC/Escolas_no_RS/MapServer/0"
ENDPOINT = SERVICE + "/query"
WHERE = "(cod_ibge_mun IN (430460,4304606) OR UPPER(municipio) = 'CANOAS')"
FIELDS = "codigo_inep,escola,dependencia_adm,municipio,cod_ibge_mun,endereco,latitude,longitude"
STAGES = ("Educação infantil", "Ensino fundamental", "Ensino médio", "EJA", "Educação profissional")
NETWORKS = {"Municipal", "Estadual", "Federal", "Privada"}

def request_data(params: dict) -> dict:
    url = ENDPOINT + "?" + urllib.parse.urlencode({**params, "where": WHERE, "f": "json"})
    error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "WebGIS-Educacao-Canoas/0.1 (Canoas municipal open data)",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=40) as response:
                if response.status != 200:
                    raise RuntimeError(f"SEDUC HTTP {response.status}")
                content = response.read(6 * 1024 * 1024 + 1)
            if len(content) > 6 * 1024 * 1024:
                raise RuntimeError("SEDUC excedeu limite da resposta JSON")
            payload = json.loads(content.decode("utf-8"))
            if not isinstance(payload, dict) or "error" in payload:
                raise RuntimeError(f"ArcGIS REST retornou erro: {str(payload)[:500]}")
            return payload
        except Exception as exc:
            error = exc
            print(f"::warning::SEDUC tentativa {attempt + 1}: {exc}", flush=True)
            if attempt < 2:
                time.sleep(3 * (2 ** attempt))
    raise RuntimeError(f"Não foi possível consultar SEDUC: {error}")

def parse_features(payload: dict, expected: int) -> list[dict]:
    if not 30 <= expected <= 1200:
        raise ValueError(f"SEDUC: cobertura municipal suspeita: {expected}")
    features = payload.get("features")
    if not isinstance(features, list):
        raise ValueError("SEDUC: resposta sem lista de feições")
    if payload.get("exceededTransferLimit") or len(features) != expected:
        raise ValueError(f"SEDUC: paginação/cobertura incompleta: esperado {expected}, recebido {len(features)}")
    records: dict[str, dict] = {}
    invalid = 0
    for f in features:
        a = f.get("attributes") or {}
        id_value = a.get("codigo_inep")
        try:
            code = str(int(id_value))
        except (ValueError, TypeError):
            invalid += 1
            continue
        if not re.fullmatch(r"\d{8}", code):
            invalid += 1
            continue
        if a.get("cod_ibge_mun") not in (430460, 4304606) and str(a.get("municipio") or "").strip().casefold() != "canoas":
            raise ValueError(f"SEDUC: escola não pertence a Canoas: INEP {code}")
        network = str(a.get("dependencia_adm") or "").strip().title()
        if network not in NETWORKS:
            invalid += 1
            continue
        geometry = f.get("geometry") or {}
        try:
            lat = float(geometry.get("y"))
            lon = float(geometry.get("x"))
        except (TypeError, ValueError):
            invalid += 1
            continue
        if not (-30.12 <= lat <= -29.72 and -51.42 <= lon <= -50.92):
            invalid += 1
            continue
        if code in records:
            raise ValueError("SEDUC: Código INEP duplicado: " + code)
        records[code] = {
            "inep": code, "name": str(a.get("escola") or "Nome não informado").strip(),
            "network": network,
            "address": str(a.get("endereco") or "").strip() or None,
            "latitude": lat, "longitude": lon,
        }
    if invalid > expected * 0.15 or len(records) < 30:
        raise ValueError(f"SEDUC: muitos registros inválidos: {invalid}/{expected}")
    return sorted(records.values(), key=lambda x: x["inep"])

def combine(existing: dict, source: list[dict]) -> tuple[dict, dict]:
    old = existing.get("schools", [])
    current_year = existing.get("year")
    catalog = {s["inep"]: s for s in old}
    matches, supplemented = 0, 0
    if current_year == 2025 and catalog:
        for item in source:
            school = catalog.get(item["inep"])
            if school is None:
                continue
            matches += 1
            if school.get("latitude") is None or school.get("longitude") is None:
                school["latitude"], school["longitude"] = item["latitude"], item["longitude"]
                school["coordinateSource"] = "SEDUC/RS · escolas do RS · INEP 2023"
                supplemented += 1
        # A edição 2025 permanece base cadastral; novas escolas de 2023 não são inseridas.
        return existing, {"matchedINEP": matches, "supplementedCoordinates": supplemented,
                          "unmatchedRS": len(source)-matches, "mode": "2025-enrichment"}
    if current_year not in (None, 2023):
        raise ValueError(f"Não é seguro mesclar catálogo de ano não reconhecido: {current_year}")
    defaults = {k: None for k in STAGES}
    rows = []
    for item in source:
        rows.append({
            **item, "year": 2023, "city": "Canoas",
            "status": "Não informado",
            "neighborhood": None,
            "enrollments": None,
            "teacherFunctions": None,
            "stages": defaults.copy(),
            "infrastructure": {},
            "coordinateSource": "SEDUC/RS · escolas do RS · INEP 2023",
        })
    rows.sort(key=lambda x: (x["name"].casefold(), x["inep"]))
    return {"schemaVersion": 1, "year": 2023,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "schools": rows,
            "note": "Cadastro PARCIAL de escolas georreferenciadas disponibilizadas na IDE/RS (referência 2023). Não equivale ao universo do Censo Escolar 2025."}, {
        "matchedINEP": 0, "supplementedCoordinates": len(rows),
        "unmatchedRS": 0, "mode": "2023-map-only",
    }

def main() -> None:
    count = request_data({"returnCountOnly": "true"})
    expected = count.get("count")
    if not isinstance(expected, int):
        raise ValueError(f"SEDUC: sem contagem de controle na fonte: {count}")
    features = request_data({"outFields": FIELDS,
                             "returnGeometry": "true",
                             "outSR": "4326",
                             "resultRecordCount": "1200"})
    source = parse_features(features, expected)
    initial = json.loads((DATA / "schools.json").read_text(encoding="utf-8"))
    schools, diagnostics = combine(initial, source)
    summary = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    summary.setdefault("sourceInfo", {})["seduc"] = {
        "status": "ok",
        "reference": "2023 · coordenadas de escolas",
        "url": SERVICE,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "note": f"{len(source)} escolas georreferenciadas na camada; {diagnostics['matchedINEP']} correspondências com o INEP 2025; {diagnostics['supplementedCoordinates']} posições complementadas. Não representa universo municipal completo.",
    }
    geo = {"type": "FeatureCollection", "features": [
        {"type": "Feature",
         "properties": {"inep": s["inep"], "name": s["name"], "network": s["network"]},
         "geometry": {"type": "Point", "coordinates": [s["longitude"], s["latitude"]]}}
        for s in schools["schools"]
        if s.get("longitude") is not None and s.get("latitude") is not None
    ]}
    provenance = {"source": SERVICE, "referenceYear": 2023,
                  "retrievedAt": summary["sourceInfo"]["seduc"]["updatedAt"],
                  "query": WHERE, "records": len(source), "expectedRecords": expected, **diagnostics}
    files = {"schools.json": schools, "schools.geojson": geo, "summary.json": summary,
             "seduc_provenance.json": provenance}
    DATA.mkdir(exist_ok=True, parents=True)
    with tempfile.TemporaryDirectory(dir=DATA) as temp:
        pending = []
        for name, payload in files.items():
            output = Path(temp) / name
            output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            json.loads(output.read_text(encoding="utf-8"))
            pending.append((output, DATA/name))
        for tmp, target in pending:
            os.replace(tmp, target)
    print(f"SEDUC geolocalização: {len(source)} escolas, modo {diagnostics['mode']}, complementadas {diagnostics['supplementedCoordinates']}")

if __name__ == "__main__":
    main()
