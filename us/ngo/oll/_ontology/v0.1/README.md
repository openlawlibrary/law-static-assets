# OLL Ontology v0.1

This directory contains:

- Ontology: `us/ngo/oll/_ontology/v0.1/ontology.owl`
- SHACL shapes for deterministic dataset validation: `us/ngo/oll/_ontology/v0.1/law-rdf.shacl.ttl`

## Validate a law-rdf checkout

Use the validator tool shipped in this repo:

```bash
cd tools/law-rdf-validator
uv sync
uv run law-rdf-validate ~/oll/archive/mohicanlaw/law-rdf --report /tmp/law-rdf-shacl-report.txt
```
