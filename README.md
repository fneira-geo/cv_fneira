# CV — Fernando A. Neira Román

CV mantenido como datos estructurados (YAML) + plantillas Jinja2/LaTeX → PDF vía xelatex (macOS/Linux) o Tectonic (Windows).

## Estructura del proyecto

```
cv_fneira/
├── TODO.md                 # tareas pendientes
├── README.md               # este archivo
├── Makefile                # atajos de compilación
│
├── data/                   ← EDITAR AQUÍ para actualizar contenido
│   ├── perfil.yaml         # datos personales, título, resumen
│   ├── experiencia.yaml    # historial laboral (flag incluir_exec)
│   ├── educacion.yaml      # títulos y diplomas
│   ├── competencias.yaml   # habilidades por área (habilidades + habilidades_full)
│   ├── cursos.yaml         # formación complementaria (flag incluir_exec)
│   ├── idiomas.yaml        # idiomas (con niveles CEFR)
│   ├── publicaciones.yaml  # artículos y congresos
│   └── referencias.yaml    # referencias profesionales (flag mostrar)
│
├── templates/              ← EDITAR AQUÍ solo para cambiar diseño visual
│   ├── _preamble.tex.j2    # preámbulo compartido (fuentes, colores, márgenes)
│   ├── cv-full.tex.j2      # CV completo
│   ├── cv-exec.tex.j2      # CV ejecutivo (3 páginas máx.)
│   ├── cv-ats.tex.j2       # CV ATS-optimizado (una columna, texto plano)
│   └── styles/             # estilos visuales (tipografía + color)
│       ├── default.j2      # azul marino #1F3A5F, lmodern serif
│       └── simple.j2       # negro #000000, Computer Modern (máxima compatibilidad ATS)
│
├── fonts/                  # Google Fonts (TTF, para xelatex/fontspec)
│
├── output/                 # PDFs compilados (NO versionados)
│   ├── cv-full.pdf
│   ├── cv-full-simple.pdf
│   ├── cv-exec.pdf
│   ├── cv-exec-simple.pdf
│   ├── cv-ats.pdf
│   └── cv-ats-simple.pdf   ← recomendado para portales ATS (ONU, LinkedIn, universidades)
│
├── build.py                # script principal
├── pyproject.toml          # configuración del proyecto (uv)
└── uv.lock                 # lock file
```

---

## Configuración del entorno

```bash
uv venv .venv
source .venv/bin/activate      # macOS/Linux
uv pip install -r requirements.txt
```

### LaTeX

**macOS:**
```bash
brew install --cask mactex-no-gui
```

**Linux:**
```bash
sudo apt-get install texlive-xetex texlive-latex-extra
```

**Windows:**
```bash
scoop install tectonic
```

---

## Compilar

```bash
make            # genera cv-full, cv-exec, cv-ats (estilo default)
make full       # solo cv-full.pdf
make exec       # solo cv-exec.pdf
make ats        # solo cv-ats.pdf
make simple     # genera las tres versiones con estilo simple

# o directamente:
uv run python build.py
uv run python build.py --full
uv run python build.py --exec
uv run python build.py --ats
uv run python build.py --style simple
```

---

## Versiones

### cv-full
CV completo. Incluye todas las entradas de experiencia, publicaciones, cursos y formación.

### cv-exec
Versión ejecutiva de máximo 3 páginas. Muestra solo entradas con `incluir_exec: true` en `experiencia.yaml` y `cursos.yaml`. Las entradas excluidas aparecen como lista compacta al final de la sección de experiencia.

### cv-ats
CV optimizado para Applicant Tracking Systems (ATS). Una columna garantizada, URLs completas visibles, sin elementos de layout que rompan parsers. Usar para portales de aplicación online (ONU, LinkedIn, universidades).

**Verificación manual:**
```bash
pdftotext output/cv-ats-simple.pdf - | head -40
```
El flujo debe ser: nombre → contacto → resumen → experiencia → educación → competencias.

---

## Estilos visuales

| Estilo | Fuente | Acento | ATS-safe |
|--------|--------|--------|----------|
| **default** | lmodern (serif) | Azul marino `#1F3A5F` | Parcial |
| **simple** | Computer Modern (serif) | Negro `#000000` | Sí |

```bash
uv run python build.py --style simple
uv run python build.py --full --style simple
```

---

## Flags de contenido

### `incluir_exec` (experiencia.yaml, cursos.yaml)

- `true` → aparece en cv-exec
- `false` → solo en cv-full (aparece como línea compacta en cv-exec)

### `habilidades_full` (competencias.yaml)

Herramientas legacy o de uso esporádico. Se renderizan solo en cv-full.

### `mostrar` (referencias.yaml)

Controla qué referencias aparecen. La sección está comentada por defecto en cv-full.tex.j2.

---

## Notas sobre las plantillas Jinja2

- Delimitadores: `[[ var ]]` y `[% block %]` (evitan conflicto con llaves LaTeX `{}`)
- Filtro `| e`: escapa caracteres especiales de LaTeX (`&`, `%`, `$`, `#`, `_`)
- Filtro `| date`: convierte `YYYY-MM` → texto en español (`2020-03` → `marzo 2020`)

---

## Flujo de trabajo

1. Editar YAML en `data/`
2. `make` o `uv run python build.py`
3. Verificar PDFs en `output/`
4. Commit con mensaje descriptivo
