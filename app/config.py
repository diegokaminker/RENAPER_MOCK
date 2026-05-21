import os

MOCK_USER = os.environ.get("MOCK_USER", "mock_user")
MOCK_PASS = os.environ.get("MOCK_PASS", "mock_pass")

PATIENT_DNI_MIN = 99_000_000
PATIENT_DNI_MAX = 99_000_999

VALID_SEXO = frozenset({"F", "M", "X"})
