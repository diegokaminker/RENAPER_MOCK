# Manual de uso — Mock RENAPER

Servicio de prueba que simula una consulta a RENAPER. Devuelve datos de persona en JSON o un código de error en el campo `resultado`.

**URL del servicio (producción):**

`https://renaper-mock-569660039899.us-central1.run.app`

---

## 1. Resumen

| Concepto | Detalle |
|----------|---------|
| Método | `GET` |
| Consulta de persona | `/renaper/obtener` |
| Estado del servicio | `/health` |
| Formato de respuesta | JSON (`Content-Type: application/json; charset=utf-8`) |
| Pacientes de prueba | 1000 DNIs sintéticos: `99000000` a `99000999` |
| Credenciales por defecto | Usuario `mock_user`, clave `mock_pass` |

Este mock **no** replica el XML ni los campos adicionales de SISA. Solo devuelve identidad básica o un error.

---

## 2. Autenticación

Cada consulta debe incluir:

| Parámetro | Descripción |
|-----------|-------------|
| `usuario` | Usuario autorizado (variable de entorno `MOCK_USER` en el servidor) |
| `clave` | Contraseña (variable `MOCK_PASS`) |

Si `usuario` o `clave` no coinciden con la configuración del servicio, la respuesta es:

```json
{ "resultado": "ERROR_AUTENTICACION" }
```

**Importante:** Si al desplegar en Cloud Run usó otros valores en `--set-env-vars`, debe usar esos mismos valores en sus llamadas. Los valores de demostración son `mock_user` y `mock_pass`.

---

## 3. Consulta de una persona

### URL completa (ejemplo)

```
GET https://renaper-mock-569660039899.us-central1.run.app/renaper/obtener?usuario=mock_user&clave=mock_pass&nrodoc=99000000&sexo=F
```

### Parámetros de consulta

| Parámetro | Obligatorio | Descripción |
|-----------|-------------|-------------|
| `usuario` | Sí | Credencial de acceso |
| `clave` | Sí | Credencial de acceso |
| `nrodoc` | Sí | Número de documento (DNI), solo dígitos |
| `sexo` | Sí | `F`, `M` o `X`. Debe coincidir con el registro almacenado |

### Respuesta exitosa (HTTP 200)

Cuando la persona existe y el `sexo` coincide:

```json
{
  "nroDocumento": "99000000",
  "apellido": "LOPEZ",
  "nombre": "AGUSTINA",
  "sexo": "F",
  "fechanacimiento": "09-10-1951"
}
```

| Campo | Descripción |
|-------|-------------|
| `nroDocumento` | DNI consultado |
| `apellido` | Uno o dos apellidos separados por un espacio (ej. `GONZALEZ PEREZ`) |
| `nombre` | Uno o dos nombres separados por un espacio (ej. `JUAN CARLOS`) |
| `sexo` | `F`, `M` o `X` |
| `fechanacimiento` | Fecha en formato `dd-mm-aaaa` |

### Respuesta con error (HTTP 200)

Solo incluye el campo `resultado`:

```json
{ "resultado": "REGISTRO_NO_ENCONTRADO" }
```

---

## 4. Códigos de error (`resultado`)

| Código | Cuándo ocurre |
|--------|----------------|
| `REGISTRO_NO_ENCONTRADO` | El DNI no está en el rango de pacientes de prueba (`99000000`–`99000999`) |
| `ERROR_AUTENTICACION` | `usuario` o `clave` incorrectos |
| `ERROR_DATOS` | Falta `nrodoc` o `sexo`, DNI no numérico, `sexo` inválido (distinto de F/M/X), o `sexo` no coincide con el registro |
| `NO_TIENE_QUOTA_DISPONIBLE` | DNI de prueba `99001000` |
| `SERVICIO_RENAPER_NO_DISPONIBLE` | DNI de prueba `99001001` |
| `MULTIPLE_RESULTADO` | DNI de prueba `99001002` |
| `ERROR_INESPERADO` | DNI de prueba `99001003` |

Los DNIs `99001000` a `99001003` sirven **solo** para simular esos errores; no representan personas reales en el padrón.

---

## 5. Datos sintéticos de prueba

- **Cantidad:** 1000 personas con DNI del `99000000` al `99000999`.
- **Nacionalidad:** datos ficticios con nombres y apellidos argentinos.
- **Apellidos y nombres compuestos:** aproximadamente el 35 % tiene dos apellidos y el 35 % dos nombres, unidos con un espacio.
- **Sexo `X`:** aproximadamente 1 de cada 7 registros (por ejemplo DNI `99000006` con `sexo=X`).

### Ejemplos de DNIs útiles

| DNI | Uso |
|-----|-----|
| `99000000` | Mujer (`sexo=F`); consulta exitosa con `sexo=F` |
| `99000006` | Persona con `sexo=X`; consulta exitosa con `sexo=X` |
| `12345678` | No existe → `REGISTRO_NO_ENCONTRADO` |
| `99001000`–`99001003` | Errores específicos (ver tabla anterior) |


## 6. Ejemplos con curl

Reemplace la URL base si ejecuta el servicio en su máquina (`http://127.0.0.1:8080`).

```bash
BASE="https://renaper-mock-569660039899.us-central1.run.app/renaper/obtener"

# Persona encontrada (99000000 es F)
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99000000&sexo=F"

# No encontrada
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=12345678&sexo=M"

# Credenciales incorrectas
curl -s "$BASE?usuario=mock_user&clave=incorrecta&nrodoc=99000000&sexo=F"

# Falta nrodoc
curl -s "$BASE?usuario=mock_user&clave=mock_pass&sexo=M"

# Falta sexo
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99000000"

# Sexo no coincide (99000000 es F, se envía M)
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99000000&sexo=M"

# Persona con sexo X
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99000006&sexo=X"

# Errores simulados
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99001000&sexo=M"
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99001001&sexo=F"
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99001002&sexo=M"
curl -s "$BASE?usuario=mock_user&clave=mock_pass&nrodoc=99001003&sexo=F"
```

Comprobación de que el servicio está activo:

```bash
curl -s "https://renaper-mock-569660039899.us-central1.run.app/health"
```

Respuesta esperada: `{"status":"ok"}`

---

## 7. Uso con Postman

1. En Postman: **Import** → seleccione el archivo  
   `postman/RENAPER-Mock.postman_collection.json`
2. Abra la colección **RENAPER Mock** → pestaña **Variables**.
3. Verifique:
   - `baseUrl` = `https://renaper-mock-569660039899.us-central1.run.app`
   - `usuario` = `mock_user`
   - `clave` = `mock_pass`
4. Ejecute las carpetas **Search — success** y **Search — errors** para probar cada escenario.

Si recibe `ERROR_AUTENTICACION` con `mock_user` / `mock_pass`, las variables de entorno en Cloud Run no coinciden. Actualícelas o ajuste `usuario` y `clave` en Postman según su despliegue.

---

## 8. Integración en su aplicación

Configure la URL base de RENAPER en su cliente apuntando a:

```
https://renaper-mock-569660039899.us-central1.run.app/renaper/obtener
```

Parámetros de la petición `GET` (mismo esquema que el fragmento de integración):

- `usuario`, `clave`, `nrodoc`, `sexo`
- Cabecera recomendada: `Content-Type: application/json; charset=utf-8`

La respuesta es **JSON**, no XML. Debe interpretar:

- Presencia de los cinco campos de persona → consulta exitosa.
- Presencia de `resultado` → error (valores listados en la sección 4).

---

## 9. Pruebas automatizadas

```bash
# En local (sin red)
pytest tests/test_search.py -v

# Contra Cloud Run
pytest tests/test_search.py -v --cloud

# Otra URL
RENAPER_BASE_URL=https://su-servicio.run.app pytest tests/test_search.py -v
```

---

## 10. Despliegue en Cloud Run

```bash
gcloud run deploy renaper-mock \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --max-instances=1 \
  --concurrency=10 \
  --set-env-vars MOCK_USER=mock_user,MOCK_PASS=mock_pass
```

El servicio en producción está limitado a **una instancia como máximo** (`maxScale: 1`) y **concurrencia 10** (hasta 10 solicitudes simultáneas por instancia).

```bash
gcloud run services update renaper-mock --region=us-central1 --max-instances=1 --concurrency=10
```

---

## 11. Documentación en inglés

Referencia técnica breve: [README.md](README.md).
