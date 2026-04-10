# tests/

## Toy 3-locus subset

A deliberately tiny slice of the full dataset used for the **nightly CI smoke
test** (`.planning/REQUIREMENTS.md` REQ-9). The goal is not statistical
correctness — it's that every rule in `src/snakemake/` executes end-to-end
without crashing.

Planned layout:

```
tests/
├── toy_3locus/
│   ├── data/                   # tiny sumstats: 3 loci × 2 traits × 2 ancestries
│   ├── config/                 # minimal pipeline.yaml override
│   ├── expected/               # hash manifests + tiny PP.H4 reference tables
│   └── Snakefile.test          # shim that points at the toy config
└── unit/                       # pytest-style unit tests for Python helpers
```

## Running

```bash
# full end-to-end smoke (CI)
snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda -p all

# Python unit tests
pytest tests/unit/
```

This infrastructure is built in **Phase 0** — it does not exist yet.
