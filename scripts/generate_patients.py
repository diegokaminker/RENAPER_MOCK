#!/usr/bin/env python3
"""Generate deterministic synthetic Argentine patients (DNI 99000000–99000999)."""

from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "data" / "patients.json"

APELLIDOS = (
    "GONZALEZ", "RODRIGUEZ", "FERNANDEZ", "LOPEZ", "MARTINEZ", "GARCIA", "PEREZ",
    "SANCHEZ", "ROMERO", "TORRES", "DIAZ", "ALVAREZ", "RUIZ", "MORENO", "JIMENEZ",
    "MUÑOZ", "HERRERA", "CASTRO", "ORTIZ", "SILVA", "RAMOS", "MENDOZA", "VARGAS",
    "CRUZ", "GUTIERREZ", "MORALES", "REYES", "FLORES", "HERRERA", "SUAREZ", "ACOSTA",
    "MEDINA", "AGUILAR", "VEGA", "CABRERA", "RIOS", "IBARRA", "PAREDES", "CAMPOS",
)

NOMBRES_M = (
    "JUAN", "JOSE", "CARLOS", "LUIS", "MIGUEL", "PEDRO", "DIEGO", "MARTIN", "PABLO",
    "ANDRES", "JORGE", "RICARDO", "FERNANDO", "SERGIO", "DANIEL", "ALEJANDRO", "MARCELO",
    "GUSTAVO", "RODRIGO", "NICOLAS", "MATIAS", "FACUNDO", "AGUSTIN", "LEONARDO", "EMILIANO",
)

NOMBRES_F = (
    "MARIA", "ANA", "LAURA", "SILVIA", "CLAUDIA", "ANDREA", "PATRICIA", "MONICA",
    "VERONICA", "CAROLINA", "GABRIELA", "VALERIA", "PAULA", "ROMINA", "FLORENCIA",
    "CAMILA", "SOFIA", "LUCIA", "JULIETA", "MARTINA", "AGUSTINA", "VICTORIA", "ELENA",
    "BEATRIZ", "NATALIA",
)


def _fecha_nacimiento(rng: random.Random) -> str:
    start = date(1940, 1, 1)
    end = date(2005, 12, 31)
    days = (end - start).days
    born = start + timedelta(days=rng.randint(0, days))
    return born.strftime("%d-%m-%Y")


def _two_parts(rng: random.Random, pool: tuple[str, ...]) -> str:
    """Pick two distinct values and join with a single space (e.g. GONZALEZ PEREZ)."""
    first = rng.choice(pool)
    second = first
    while second == first and len(pool) > 1:
        second = rng.choice(pool)
    return f"{first} {second}"


def _maybe_compound(rng: random.Random, pool: tuple[str, ...], chance: float) -> str:
    if rng.random() < chance:
        return _two_parts(rng, pool)
    return rng.choice(pool)


def _sexo_for_dni(dni: int) -> str:
    if dni % 7 == 0:
        return "X"
    return "F" if dni % 2 == 0 else "M"


def _patient(dni: int) -> dict[str, str]:
    rng = random.Random(dni)
    sexo = _sexo_for_dni(dni)
    if sexo == "F":
        nombres_pool = NOMBRES_F
    elif sexo == "M":
        nombres_pool = NOMBRES_M
    else:
        nombres_pool = NOMBRES_F + NOMBRES_M
    # ~35% double apellido, ~35% double nombre (some have both).
    apellido = _maybe_compound(rng, APELLIDOS, 0.35)
    nombre = _maybe_compound(rng, nombres_pool, 0.35)
    doc = str(dni)
    return {
        "nroDocumento": doc,
        "apellido": apellido,
        "nombre": nombre,
        "sexo": sexo,
        "fechanacimiento": _fecha_nacimiento(rng),
    }


def main() -> None:
    patients: dict[str, dict[str, str]] = {}
    for dni in range(99_000_000, 99_001_000):
        patient = _patient(dni)
        patients[patient["nroDocumento"]] = patient
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(patients, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {len(patients)} patients to {OUTPUT}")


if __name__ == "__main__":
    main()
