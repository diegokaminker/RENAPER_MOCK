from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Union

from app.config import MOCK_PASS, MOCK_USER, PATIENT_DNI_MAX, PATIENT_DNI_MIN, VALID_SEXO

# Trigger DNIs outside the 1000-patient range (99000000–99000999).
TRIGGER_DNIS: dict[str, str] = {
    "99001000": "NO_TIENE_QUOTA_DISPONIBLE",
    "99001001": "SERVICIO_RENAPER_NO_DISPONIBLE",
    "99001002": "MULTIPLE_RESULTADO",
    "99001003": "ERROR_INESPERADO",
}


@dataclass(frozen=True)
class SearchSuccess:
    patient: dict[str, str]


@dataclass(frozen=True)
class SearchError:
    resultado: str


SearchResult = Union[SearchSuccess, SearchError]


def _normalize_nrodoc(nrodoc: Optional[str]) -> Optional[str]:
    if nrodoc is None:
        return None
    value = nrodoc.strip()
    return value or None


def _normalize_sexo(sexo: Optional[str]) -> Optional[str]:
    if sexo is None:
        return None
    value = sexo.strip().upper()
    return value or None


def _is_valid_dni(nrodoc: str) -> bool:
    return nrodoc.isdigit()


def _dni_in_patient_range(nrodoc: str) -> bool:
    if not _is_valid_dni(nrodoc):
        return False
    n = int(nrodoc)
    return PATIENT_DNI_MIN <= n <= PATIENT_DNI_MAX


def search(
    *,
    usuario: Optional[str],
    clave: Optional[str],
    nrodoc: Optional[str],
    sexo: Optional[str],
    patients: dict[str, dict[str, str]],
) -> SearchResult:
    if usuario != MOCK_USER or clave != MOCK_PASS:
        return SearchError("ERROR_AUTENTICACION")

    doc = _normalize_nrodoc(nrodoc)
    if doc is None or not _is_valid_dni(doc):
        return SearchError("ERROR_DATOS")

    sex = _normalize_sexo(sexo)
    if sex is None or sex not in VALID_SEXO:
        return SearchError("ERROR_DATOS")

    if doc in TRIGGER_DNIS:
        return SearchError(TRIGGER_DNIS[doc])

    patient = patients.get(doc)
    if patient is None:
        if _dni_in_patient_range(doc):
            return SearchError("REGISTRO_NO_ENCONTRADO")
        return SearchError("REGISTRO_NO_ENCONTRADO")

    if sex != patient["sexo"]:
        return SearchError("ERROR_DATOS")

    return SearchSuccess(patient=dict(patient))


def to_response_body(result: SearchResult) -> dict[str, Any]:
    if isinstance(result, SearchSuccess):
        return result.patient
    return {"resultado": result.resultado}
