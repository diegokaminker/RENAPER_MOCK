# RENAPER mock (Google Cloud Run)

Mock RENAPER lookup API returning JSON with person fields or a `resultado` error.

**Manual de uso en español:** [README.es.md](README.es.md)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/renaper/obtener` | Search by DNI |
| GET | `/health` | Health check |

### Query parameters

- `usuario` (required) — must match `MOCK_USER`
- `clave` (required) — must match `MOCK_PASS`
- `nrodoc` (required) — DNI to look up
- `sexo` (required) — `F`, `M`, or `X`; must match stored patient or returns `ERROR_DATOS`

### Success response (200)

```json
{
  "nroDocumento": "99000000",
  "apellido": "GONZALEZ",
  "nombre": "JUAN",
  "sexo": "M",
  "fechanacimiento": "12-08-1972"
}
```

### Error response (200)

```json
{ "resultado": "REGISTRO_NO_ENCONTRADO" }
```

### Synthetic patients

- **1000** records: DNI `99000000`–`99000999`
- Regenerate: `python3 scripts/generate_patients.py`
- ~35% have two apellidos (`GONZALEZ PEREZ`) and ~35% two nombres (`JUAN CARLOS`), joined with a single space; some have both
- `sexo` is `F`, `M`, or `X` (~1/7 of patients use `X`, e.g. DNI `99000006`)

### Trigger DNIs (errors only)

| `nrodoc` | `resultado` |
|----------|-------------|
| `99001000` | `NO_TIENE_QUOTA_DISPONIBLE` |
| `99001001` | `SERVICIO_RENAPER_NO_DISPONIBLE` |
| `99001002` | `MULTIPLE_RESULTADO` |
| `99001003` | `ERROR_INESPERADO` |

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/generate_patients.py
uvicorn app.main:app --reload --port 8080
```

### Tests

```bash
# Local (in-process)
pytest tests/test_search.py -v

# Against Cloud Run
pytest tests/test_search.py -v --cloud

# Custom URL
RENAPER_BASE_URL=https://your-service.run.app pytest tests/test_search.py -v
```

### Postman

Import [postman/RENAPER-Mock.postman_collection.json](postman/RENAPER-Mock.postman_collection.json) into Postman.

Collection variable `baseUrl` is preset to:

`https://renaper-mock-569660039899.us-central1.run.app`

Default collection credentials: `mock_user` / `mock_pass` (must match Cloud Run `MOCK_USER` / `MOCK_PASS`).

### curl examples

```bash
BASE="http://127.0.0.1:8080/renaper/obtener"

# Found (99000000 is F)
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99000000&sexo=F" | jq .

# Not found
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=12345678&sexo=M" | jq .

# Bad credentials
curl -s "$BASE?usuario=mock_user&clave=wrong&nrodoc=99000000&sexo=F" | jq .

# Missing nrodoc
curl -s "$BASE?usuario=mock_user&clave=mock_pass&sexo=M" | jq .

# Missing sexo
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99000000" | jq .

# Invalid nrodoc
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=abc&sexo=F" | jq .

# Sexo mismatch (99000000 is F)
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99000000&sexo=M" | jq .

# Trigger errors
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99001000&sexo=M" | jq .
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99001001&sexo=F" | jq .
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99001002&sexo=M" | jq .
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99001003&sexo=F" | jq .
```

## Google Cloud Run

```bash
gcloud run deploy renaper-mock \
  --source . \
  --region YOUR_REGION \
  --allow-unauthenticated \
  --max-instances=1 \
  --concurrency=10 \
  --set-env-vars MOCK_USER=mock_user,MOCK_PASS=mock_pass
```

The live service is capped at **one instance** (`maxScale: 1`) with **concurrency 10** (max 10 simultaneous requests per instance).

To update an existing service:

```bash
gcloud run services update renaper-mock --region=us-central1 --max-instances=1 --concurrency=10
```

Point your client `url` to:

`https://YOUR_SERVICE_URL/renaper/obtener`

Default credentials (local and demo): `mock_user` / `mock_pass`.
