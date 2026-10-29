# lean-env-action

Reusable GitHub Actions for setting up a [Lean 4](https://lean-lang.org) toolchain
with the [Mathlib](https://github.com/leanprover-community/mathlib4) build cache, and
for building a [leanblueprint](https://github.com/PatrickMassot/leanblueprint).

This repository hosts three composite actions:

| Action | Reference | What it does |
| --- | --- | --- |
| **Setup Lean Environment** | `texra-ai/lean-env-action@main` | Lean toolchain + Mathlib build cache. |
| **Blueprint system deps** | `texra-ai/lean-env-action/blueprint-system-deps@main` | TeX / dvisvgm / Graphviz apt packages, with an apt archive cache. |
| **Install leanblueprint** | `texra-ai/lean-env-action/leanblueprint@main` | Python 3.12 + the `leanblueprint` toolchain. |

The actions are orthogonal and self-contained: use the one you need, or compose
them for blueprint workflows. The leanblueprint install lives in exactly one
place (the `leanblueprint` action), so there is nothing to keep in sync.

## Setup Lean Environment

Sets up the Lean toolchain pinned by your `lean-toolchain` and restores the
Mathlib build cache.

```yaml
steps:
  - uses: actions/checkout@v6
  - uses: texra-ai/lean-env-action@main
  - run: lake build
```

| Input | Default | Description |
| --- | --- | --- |
| `use-github-cache` | `true` | Forward to `lean-action`'s GitHub caching of `.lake`. |

For blueprint tooling, add the `leanblueprint` action (and `blueprint-system-deps`
too if you compile the blueprint):

```yaml
steps:
  - uses: actions/checkout@v6
  - uses: texra-ai/lean-env-action@main
  - uses: texra-ai/lean-env-action/leanblueprint@main
  - run: lake exe checkdecls blueprint/lean_decls
```

## Blueprint system deps

Installs the TeX / dvisvgm / Graphviz packages needed to compile a blueprint,
caching the downloaded `.deb` archives so repeat runs are fast.
The action refreshes apt indexes before restoring the cache. Its immutable save
key includes the index contents, the action's package definition and
`extra-packages`, so updated Ubuntu packages can be saved under a fresh key.
When that key is new, it restores the most recent archives for the same package
set, including the earlier fixed-key cache, and downloads only missing versions.
The archive directory stays the same across these cache generations.

```yaml
steps:
  - uses: texra-ai/lean-env-action/blueprint-system-deps@main
    with:
      cache-suffix: pdf-v1            # optional, distinguishes package sets
      extra-packages: texlive-science # optional, space-separated
```

| Input | Default | Description |
| --- | --- | --- |
| `cache-suffix` | `web-v1` | Distinguishes this package set in the apt archive cache key. |
| `extra-packages` | `''` | Additional apt packages, space-separated. |

The base set is: `chktex`, `dvisvgm`, `graphviz`, `latexmk`, `libgraphviz-dev`,
`texlive-extra-utils`, `texlive-fonts-recommended`, `texlive-latex-extra`,
`texlive-pictures`, `texlive-xetex`.

## Install leanblueprint

Installs Python 3.12 and the `leanblueprint` toolchain (plus the Graphviz headers
it builds against). This is the single home for the leanblueprint install.

```yaml
steps:
  - uses: texra-ai/lean-env-action/leanblueprint@main
```

| Input | Default | Description |
| --- | --- | --- |
| `extra-pip-packages` | `''` | Additional pip packages, space-separated. |

`pybtex` is pinned to `0.26.1`: newer releases break plastex bibliography rendering.

## Compiling a blueprint

A full `leanblueprint web` / `leanblueprint pdf` job composes the TeX stack and
the Python tool:

```yaml
steps:
  - uses: actions/checkout@v6
  - uses: texra-ai/lean-env-action/blueprint-system-deps@main
  - uses: texra-ai/lean-env-action/leanblueprint@main
  - working-directory: blueprint
    run: |
      leanblueprint pdf
      leanblueprint web
```

## Versioning

The examples pin `@main`. For reproducible CI, pin a tag or a full commit SHA
once releases are published.

## License

[Apache-2.0](LICENSE).
