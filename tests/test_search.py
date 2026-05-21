from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

import pytest

PATIENTS_PATH = Path(__file__).resolve().parent.parent / "data" / "patients.json"
PERSON_FIELDS = frozenset(
    {"nroDocumento", "apellido", "nombre", "sexo", "fechanacimiento"}
)


def _get(client, params: Optional[Dict[str, str]] = None):
    return client.get("/renaper/obtener", params=params or {})


def _assert_error_only(response, resultado: str) -> None:
    assert response.status_code == 200
    body = response.json()
    assert body == {"resultado": resultado}


@pytest.fixture(scope="module")
def sample_patient() -> Dict[str, str]:
    with PATIENTS_PATH.open(encoding="utf-8") as f:
        patients = json.load(f)
    return patients["99000000"]


def test_search_found_returns_person_fields(
    client, auth_params: Dict[str, str], sample_patient: Dict[str, str]
) -> None:
    response = _get(
        client,
        {**auth_params, "nrodoc": "99000000", "sexo": sample_patient["sexo"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == PERSON_FIELDS
    assert body == sample_patient


def test_search_not_found(client, auth_params: Dict[str, str]) -> None:
    response = _get(client, {**auth_params, "nrodoc": "12345678", "sexo": "M"})
    _assert_error_only(response, "REGISTRO_NO_ENCONTRADO")


def test_search_bad_credentials(client, auth_params: Dict[str, str]) -> None:
    response = _get(
        client, {**auth_params, "clave": "wrong", "nrodoc": "99000000", "sexo": "F"}
    )
    _assert_error_only(response, "ERROR_AUTENTICACION")


def test_search_missing_nrodoc(client, auth_params: Dict[str, str]) -> None:
    response = _get(client, {**auth_params, "sexo": "M"})
    _assert_error_only(response, "ERROR_DATOS")


def test_search_missing_sexo(client, auth_params: Dict[str, str]) -> None:
    response = _get(client, {**auth_params, "nrodoc": "99000000"})
    _assert_error_only(response, "ERROR_DATOS")


def test_search_invalid_nrodoc(client, auth_params: Dict[str, str]) -> None:
    response = _get(client, {**auth_params, "nrodoc": "abc", "sexo": "F"})
    _assert_error_only(response, "ERROR_DATOS")


def test_search_sexo_mismatch(
    client, auth_params: Dict[str, str], sample_patient: Dict[str, str]
) -> None:
    stored = sample_patient["sexo"]
    wrong = "M" if stored == "F" else "F"
    response = _get(client, {**auth_params, "nrodoc": "99000000", "sexo": wrong})
    _assert_error_only(response, "ERROR_DATOS")


def test_search_invalid_sexo(client, auth_params: Dict[str, str]) -> None:
    response = _get(client, {**auth_params, "nrodoc": "99000000", "sexo": "Z"})
    _assert_error_only(response, "ERROR_DATOS")


def test_search_found_with_sexo_x(client, auth_params: Dict[str, str]) -> None:
    """99000006 is deterministic sexo X (dni % 7 == 0)."""
    with PATIENTS_PATH.open(encoding="utf-8") as f:
        patient = json.load(f)["99000006"]
    assert patient["sexo"] == "X"
    response = _get(
        client, {**auth_params, "nrodoc": "99000006", "sexo": "X"}
    )
    assert response.status_code == 200
    assert response.json() == patient


def test_search_no_quota(client, auth_params: Dict[str, str]) -> None:
    response = _get(client, {**auth_params, "nrodoc": "99001000", "sexo": "M"})
    _assert_error_only(response, "NO_TIENE_QUOTA_DISPONIBLE")


def test_search_service_unavailable(client, auth_params: Dict[str, str]) -> None:
    response = _get(client, {**auth_params, "nrodoc": "99001001", "sexo": "F"})
    _assert_error_only(response, "SERVICIO_RENAPER_NO_DISPONIBLE")


def test_search_multiple_resultado(client, auth_params: Dict[str, str]) -> None:
    response = _get(client, {**auth_params, "nrodoc": "99001002", "sexo": "M"})
    _assert_error_only(response, "MULTIPLE_RESULTADO")


def test_search_error_inesperado(client, auth_params: Dict[str, str]) -> None:
    response = _get(client, {**auth_params, "nrodoc": "99001003", "sexo": "F"})
    _assert_error_only(response, "ERROR_INESPERADO")
