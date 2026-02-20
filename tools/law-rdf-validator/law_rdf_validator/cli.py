from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rdflib import Graph
from pyshacl import validate


def _find_repo_root(start: Path) -> Path | None:
    """Walk upwards until we find the ontology+shapes paths."""
    want_shapes = Path("us/ngo/oll/_ontology/v0.1/law-rdf.shacl.ttl")
    want_owl = Path("us/ngo/oll/_ontology/v0.1/ontology.owl")
    cur = start
    while True:
        if (cur / want_shapes).exists() and (cur / want_owl).exists():
            return cur
        if cur.parent == cur:
            return None
        cur = cur.parent


def _load_data_graph(
    data_path: Path, *, format_hint: str | None = None
) -> tuple[Graph, int]:
    g = Graph()
    parse_errors = 0

    if data_path.is_dir():
        rdf_files = sorted(data_path.rglob("*.rdf"))
        if not rdf_files:
            raise ValueError(f"No .rdf files found under {data_path}")
        for f in rdf_files:
            try:
                g.parse(f.as_posix(), format=format_hint)
            except Exception as e:
                parse_errors += 1
                print(f"[PARSE ERROR] {f}: {e}", file=sys.stderr)
    else:
        g.parse(data_path.as_posix(), format=format_hint)

    return g, parse_errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a law-rdf dataset against SHACL shapes"
    )
    parser.add_argument("data", help="Path to law-rdf folder or a single RDF file")
    parser.add_argument(
        "--shapes",
        help="Path to SHACL shapes TTL (defaults to repo's law-rdf.shacl.ttl)",
        default=None,
    )
    parser.add_argument(
        "--ontology",
        help="Path to ontology OWL (optional; used as ont_graph for inference)",
        default=None,
    )
    parser.add_argument(
        "--inference",
        choices=["none", "rdfs"],
        default="rdfs",
        help="Inference level for SHACL validation",
    )
    parser.add_argument(
        "--report",
        help="Write text report to this path",
        default=None,
    )
    parser.add_argument(
        "--format",
        help="Optional rdflib parse format hint (e.g., 'xml')",
        default=None,
    )

    args = parser.parse_args(argv)
    data_path = Path(args.data).expanduser().resolve()
    if not data_path.exists():
        print(f"Data path not found: {data_path}", file=sys.stderr)
        return 2

    # Resolve defaults from repo root
    repo_root = _find_repo_root(Path(__file__).resolve())
    if repo_root is None:
        repo_root = _find_repo_root(Path.cwd())

    shapes_path: Path | None
    ontology_path: Path | None

    if args.shapes is None:
        if repo_root is None:
            print("Unable to locate repo root; provide --shapes", file=sys.stderr)
            return 2
        shapes_path = repo_root / "us/ngo/oll/_ontology/v0.1/law-rdf.shacl.ttl"
    else:
        shapes_path = Path(args.shapes).expanduser().resolve()

    if args.ontology is None:
        ontology_path = None
        if repo_root is not None:
            candidate = repo_root / "us/ngo/oll/_ontology/v0.1/ontology.owl"
            if candidate.exists():
                ontology_path = candidate
    else:
        ontology_path = Path(args.ontology).expanduser().resolve()

    if not shapes_path.exists():
        print(f"Shapes file not found: {shapes_path}", file=sys.stderr)
        return 2

    try:
        data_g, parse_errors = _load_data_graph(data_path, format_hint=args.format)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 2

    shapes_g = Graph().parse(shapes_path.as_posix(), format="turtle")
    ont_g = None
    if ontology_path is not None and ontology_path.exists():
        try:
            ont_g = Graph().parse(ontology_path.as_posix())
        except Exception as e:
            print(f"[ONTOLOGY PARSE ERROR] {ontology_path}: {e}", file=sys.stderr)
            return 2

    conforms, _, report_text = validate(
        data_graph=data_g,
        shacl_graph=shapes_g,
        ont_graph=ont_g,
        inference=None if args.inference == "none" else args.inference,
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
        meta_shacl=False,
        advanced=True,
        js=False,
        debug=False,
    )

    if args.report:
        report_path = Path(args.report).expanduser().resolve()
        report_path.write_text(report_text, encoding="utf-8")
        print(f"Report: {report_path}")

    print(f"Conforms: {conforms}")
    if parse_errors:
        print(f"Parse errors: {parse_errors}")

    if conforms:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
