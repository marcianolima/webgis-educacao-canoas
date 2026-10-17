#!/usr/bin/env python3
"""Coleta Censo Escolar 2025: apenas dados públicos agregados e cadastrais.
O layout é inspecionado em tempo de execução: campos obrigatórios ausentes impedem
a publicação, enquanto campos opcionais ausentes permanecem como null.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tempfile
import time
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timezone

YEAR = 2025
URL = "https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2025_.zip"
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"
MAX_COMPRESSED = int(os.environ.get("INEP_MAX_ZIP_MB", "850")) * 1024 * 1024
MAX_EXTRACTED = int(os.environ.get("INEP_MAX_CSV_MB", "3500")) * 1024 * 1024
NETWORKS = {"1": "Federal", "2": "Estadual", "3": "Municipal", "4": "Privada"}
STAGES = {
    "Educação infantil": "QT_MAT_INF",
    "Ensino fundamental": "QT_MAT_FUND",
    "Ensino médio": "QT_MAT_MED",
    "EJA": "QT_MAT_EJA",
    "Educação profissional": "QT_MAT_PROF",
}
INFRASTRUCTURE = {
    "Internet": "IN_INTERNET",
    "Biblioteca": "IN_BIBLIOTECA",
    "Sala de leitura": "IN_SALA_LEITURA",
    "Laboratório de informática": "IN_LABORATORIO_INFORMATICA",
    "Laboratório de ciências": "IN_LABORATORIO_CIENCIAS",
    "Quadra de esportes": "IN_QUADRA_ESPORTES",
    "Banheiro acessível": "IN_BANHEIRO_PNE",
    "Água potável": "IN_AGUA_POTAVEL",
    "Energia elétrica": "IN_ENERGIA_REDE_PUBLICA",
    "Esgotamento público": "IN_ESGOTO_REDE_PUBLICA",
}
REQUIRED = {"CO_ENTIDADE", "CO_MUNICIPIO", "NO_ENTIDADE", "TP_DEPENDENCIA", "TP_SITUACAO_FUNCIONAMENTO"}
CANOAS = {"430460", "4304606"}

def integer(value: str | None) -> int | None:
    if value is None or not value.strip():
        return None
    try:
        n = int(float(value.strip().replace(",", ".")))
        return n if n >= 0 else None
    except (ValueError, OverflowError):
        return None

def coordinate(value: str | None, low: float, high: float) -> float | None:
    try:
        n = float(str(value).strip().replace(",", "."))
        return n if low <= n <= high else None
    except (TypeError, ValueError):
        return None

def clean(value: str | None) -> str | None:
    value = (value or "").strip()
    return value if value else None

def flag(value: str | None) -> bool | None:
    return True if value == "1" else False if value == "0" else None

def convert_row(row: dict[str, str]) -> dict:
    code = str(row.get("CO_ENTIDADE", "")).strip()
    if not re.fullmatch(r"\d{8}", code):
        raise ValueError("Código INEP inválido no município: " + repr(code))
    dep = row["TP_DEPENDENCIA"].strip()
    if dep not in NETWORKS:
        raise ValueError("Dependência administrativa INEP desconhecida: " + repr(dep))
    lat = coordinate(row.get("NU_LATITUDE"), -30.12, -29.72)
    lon = coordinate(row.get("NU_LONGITUDE"), -51.42, -50.92)
    if lat is None or lon is None:
        lat = lon = None
    address = " ".join(filter(None, [clean(row.get("NO_ENDERECO")), clean(row.get("NU_ENDERECO"))])) or None
    return {
        "inep": code,
        "name": clean(row.get("NO_ENTIDADE")) or "Nome não informado",
        "network": NETWORKS[dep],
        "status": "Em atividade" if row["TP_SITUACAO_FUNCIONAMENTO"].strip() == "1" else "Outra situação",
        "neighborhood": clean(row.get("NO_BAIRRO")),
        "address": address,
        "city": "Canoas",
        "year": YEAR,
        "enrollments": integer(row.get("QT_MAT_BAS")),
        "stages": {name: integer(row.get(col)) for name, col in STAGES.items()},
        "infrastructure": {name: flag(row.get(col)) for name, col in INFRASTRUCTURE.items()},
        "latitude": lat,
        "longitude": lon,
        "coordinateSource": "INEP/Censo Escolar " + str(YEAR) if lat is not None else None,
    }

def transform(reader: csv.DictReader) -> tuple[list[dict], dict]:
    fields = {str(name).strip().lstrip("\ufeff") for name in reader.fieldnames or []}
    missing = REQUIRED - fields
    if missing:
        raise ValueError("Esquema INEP não compatível; colunas obrigatórias ausentes: " + ", ".join(sorted(missing)))
    data = []
    seen: set[str] = set()
    all_rows = 0
    for raw in reader:
        all_rows += 1
        if str(raw.get("CO_MUNICIPIO", "")).strip() not in CANOAS:
            continue
        item = convert_row(raw)
        if item["inep"] in seen:
            raise ValueError("Código INEP repetido para Canoas: " + item["inep"])
        seen.add(item["inep"])
        data.append(item)
    if all_rows < 100_000:
        raise ValueError(f"Cobertura nacional não comprovada: {all_rows} registros")
    if not 30 <= len(data) <= 1500:
        raise ValueError(f"Cobertura municipal suspeita: {len(data)} escolas")
    data.sort(key=lambda x: (x["name"].casefold(), x["inep"]))
    availability = {
        "observedColumns": sorted(fields),
        "missingOptionalColumns": sorted(
            ({'QT_MAT_BAS','NU_LATITUDE','NU_LONGITUDE','NO_BAIRRO','NO_ENDERECO','NU_ENDERECO'}
             | set(STAGES.values()) | set(INFRASTRUCTURE.values())) - fields
        ),
        "nationalRows": all_rows,
        "municipalRows": len(data),
        "withCoordinates": sum(x["latitude"] is not None for x in data),
        "enrollmentCoverage": sum(x["enrollments"] is not None for x in data),
    }
    return data, availability

def download(destination: Path) -> str:
    error = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(URL, headers={"User-Agent": "WebGIS-Educacao-Canoas/0.1 (+https://github.com/marcianolima/webgis-educacao-canoas)", "Accept": "application/zip,*/*"})
            with urllib.request.urlopen(request, timeout=100) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Download INEP HTTP {resp.status}")
                length = int(resp.headers.get("Content-Length") or 0)
                if length > MAX_COMPRESSED:
                    raise RuntimeError(f"Arquivo ZIP excede limite ({length} bytes)")
                digest, size = hashlib.sha256(), 0
                with destination.open("wb") as out:
                    while True:
                        chunk = resp.read(2 * 1024 * 1024)
                        if not chunk:
                            break
                        size += len(chunk)
                        if size > MAX_COMPRESSED:
                            raise RuntimeError("Download interrompido: limite de tamanho do ZIP")
                        digest.update(chunk)
                        out.write(chunk)
                if size < 1024:
                    raise RuntimeError("Download incompleto ou vazio")
                return digest.hexdigest()
        except Exception as exc:
            error = exc
            print(f"::warning::Tentativa {attempt+1}: {exc}", flush=True)
            if attempt < 2:
                time.sleep(2 ** attempt * 3)
    raise RuntimeError(f"INEP indisponível após tentativas: {error}")

def read_zip(archive: Path) -> tuple[list[dict],dict,str]:
    with zipfile.ZipFile(archive) as z:
        candidates = [
            i for i in z.infolist()
            if re.search(r"(Tabela[_ -]?Escola|microdados_ed_basica|microdados_educacao_basica|escolas)[^/]*\.csv$", i.filename, re.I)
            and not i.is_dir()
        ]
        if not candidates:
            raise RuntimeError("ZIP sem CSV cadastral escolar reconhecido: " + ", ".join(i.filename for i in z.infolist()[:20]))
        # Alguns pacotes incluem outra tabela por escola; preferir Tabela_Escola.
        candidates.sort(key=lambda i: (0 if "tabela_escola" in i.filename.lower() else 1,i.file_size))
        member = candidates[0]
        if member.file_size > MAX_EXTRACTED:
            raise RuntimeError(f"CSV excede limite descompactado: {member.file_size}")
        with z.open(member) as stream:
            preview = stream.read(10000)
        try:
            preview.decode("utf-8-sig", errors="strict")
            encoding = "utf-8-sig"
        except UnicodeDecodeError:
            encoding = "cp1252"
        with z.open(member) as stream, io.TextIOWrapper(stream, encoding=encoding, newline="", errors="replace") as text_stream:
            data, info = transform(csv.DictReader(text_stream, delimiter=";"))
        return data, info, member.filename

def build_documents(schools: list[dict], meta: dict, sha256: str, member: str) -> dict[str,dict]:
    now = datetime.now(timezone.utc).isoformat()
    network = Counter(s["network"] for s in schools)
    active = sum(s["status"] == "Em atividade" for s in schools)
    enrollment_complete = all(s["enrollments"] is not None for s in schools)
    enrollment_by_network = {
        n: sum(s["enrollments"] or 0 for s in schools if s["network"] == n)
        for n in NETWORKS.values()
    } if enrollment_complete else {}
    infra = {}
    for name in INFRASTRUCTURE:
        observations = [s["infrastructure"][name] for s in schools if s["infrastructure"][name] is not None]
        if observations:
            infra[name] = {"yes": sum(observations), "observed": len(observations)}
    summary = json.loads((DATA/"summary.json").read_text(encoding="utf-8"))
    summary["education"] = {
        "year": YEAR,
        "totalSchools": len(schools),
        "activeSchools": active,
        "totalEnrollments": sum(s["enrollments"] for s in schools) if enrollment_complete else None,
        "schoolsByNetwork": dict(network),
        "enrollmentsByNetwork": enrollment_by_network,
        "infrastructure": infra,
    }
    summary["generatedAt"] = now
    summary["sourceInfo"]["inep"] = {
        "status": "ok" if enrollment_complete else "partial",
        "reference": str(YEAR), "url": URL,
        "updatedAt": now,
        "note": f"{len(schools)} escolas, {meta['nationalRows']} linhas nacionais; matrículas: {meta['enrollmentCoverage']}/{len(schools)} escolas com valor; {meta['withCoordinates']} georreferenciadas. Colunas não encontradas: {', '.join(meta['missingOptionalColumns']) or 'nenhuma'}."
    }
    geo = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"inep": s["inep"], "name": s["name"], "network": s["network"]},
         "geometry": {"type": "Point", "coordinates": [s["longitude"], s["latitude"]]}}
        for s in schools if s["latitude"] is not None
    ]}
    return {
        "summary.json": summary,
        "schools.json": {"schemaVersion": 1, "year": YEAR, "updatedAt": now, "schools": schools,
                         "note": "Escolas do município no Censo Escolar, incluindo registros sem coordenadas. Não são estudantes únicos."},
        "schools.geojson": geo,
        "inep_provenance.json": {"source": URL, "member": member, "archiveSHA256": sha256,
                                 "year": YEAR, "retrievedAt": now, **meta},
    }

def publish(docs: dict[str,dict]) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=DATA) as temp:
        staged = []
        for name, payload in docs.items():
            path = Path(temp)/name
            path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            json.loads(path.read_text(encoding="utf-8"))
            staged.append((path,DATA/name))
        # Nenhum arquivo de saída é publicado antes da reconciliação completa.
        for source, target in staged:
            os.replace(source,target)

def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)/"microdados_inep.zip"
        sha = download(path)
        records, meta, member = read_zip(path)
        docs = build_documents(records,meta,sha,member)
        publish(docs)
    print(f"Coleta INEP {YEAR} validada: {meta['municipalRows']} escolas, {meta['withCoordinates']} com coordenadas; matrículas informadas para {meta['enrollmentCoverage']}.")
    if not meta["enrollmentCoverage"]:
        print("::warning::Arquivo de escolas não contém total de matrículas; integração matrícula-escola permanece pendente.")

if __name__ == "__main__":
    main()
