from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from app.lookup import search, to_response_body

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "patients.json"

app = FastAPI(title="RENAPER Mock", version="1.0.0")


def _load_patients() -> dict[str, dict[str, str]]:
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


PATIENTS = _load_patients()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/renaper/obtener")
def renaper_obtener(
    usuario: Optional[str] = Query(default=None),
    clave: Optional[str] = Query(default=None),
    nrodoc: Optional[str] = Query(default=None),
    sexo: Optional[str] = Query(default=None),
) -> JSONResponse:
    result = search(
        usuario=usuario,
        clave=clave,
        nrodoc=nrodoc,
        sexo=sexo,
        patients=PATIENTS,
    )
    return JSONResponse(
        content=to_response_body(result),
        media_type="application/json; charset=utf-8",
    )
