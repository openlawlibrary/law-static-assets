# law-rdf-validator

Deterministic SHACL validation for OLL `law-rdf` datasets.

This tool validates your RDF data against the SHACL shapes shipped in this repo:

- Shapes: `us/ngo/oll/_ontology/v0.1/law-rdf.shacl.ttl`
- Ontology (optional for inference): `us/ngo/oll/_ontology/v0.1/ontology.owl`

## Setup (uv)

From the repo root:

```bash
cd tools/law-rdf-validator
uv sync
```

## Validate a Dataset Folder

Example (Mohican archive):

```bash
cd tools/law-rdf-validator
uv run law-rdf-validate ~/oll/archive/mohicanlaw/law-rdf
```

## Common Options

- Write the full report to a file:

```bash
uv run law-rdf-validate ~/oll/archive/mohicanlaw/law-rdf --report /tmp/law-rdf-shacl-report.txt
```

- Validate a single RDF/XML file:

```bash
uv run law-rdf-validate ~/oll/archive/mohicanlaw/law-rdf/index.rdf
```

- Override shapes/ontology paths:

```bash
uv run law-rdf-validate ~/oll/archive/mohicanlaw/law-rdf \
  --shapes ../../us/ngo/oll/_ontology/v0.1/law-rdf.shacl.ttl \
  --ontology ../../us/ngo/oll/_ontology/v0.1/ontology.owl
```

## Exit Codes

- `0`: conforms
- `1`: does not conform (violations exist)
- `2`: usage/config/parse error
