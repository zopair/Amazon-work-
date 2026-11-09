# Dependency inventory and source-provenance audit
_Last checked: 2026-11-10_

## Python runtime lock

The print build now pins direct and transitive Python package versions in `requirements.txt`. The exact versions below were observed in the successful Python 3.12 GitHub Actions build.

| Package | Version | Upstream GitHub repository | Upstream license |
|---|---:|---|---|
| WeasyPrint | 68.1 | [Kozea/WeasyPrint](https://github.com/Kozea/WeasyPrint) | BSD-3-Clause |
| pypdf | 5.1.0 | [py-pdf/pypdf](https://github.com/py-pdf/pypdf) | BSD-3-Clause |
| pydyf | 0.13.0 | [CourtBouillon/pydyf](https://github.com/CourtBouillon/pydyf) | BSD-3-Clause |
| cffi | 2.1.1 | [python-cffi/cffi](https://github.com/python-cffi/cffi) | MIT |
| tinyhtml5 | 2.1.0 | [CourtBouillon/tinyhtml5](https://github.com/CourtBouillon/tinyhtml5) | MIT |
| tinycss2 | 1.5.1 | [Kozea/tinycss2](https://github.com/Kozea/tinycss2) | BSD-3-Clause |
| cssselect2 | 0.10.1 | [Kozea/cssselect2](https://github.com/Kozea/cssselect2) | BSD-3-Clause |
| Pyphen | 0.18.1 | [Kozea/Pyphen](https://github.com/Kozea/Pyphen) | GPL-2.0+ / LGPL-2.1+ / MPL-1.1 tri-license; bundled dictionaries have their own notices |
| Pillow | 13.0.0 | [python-pillow/Pillow](https://github.com/python-pillow/Pillow) | MIT-CMU |
| fonttools | 4.68.0 | [fonttools/fonttools](https://github.com/fonttools/fonttools) | MIT |
| pycparser | 3.12 | [eliben/pycparser](https://github.com/eliben/pycparser) | BSD-3-Clause |
| webencodings | 0.6.1 | [gsnedders/python-webencodings](https://github.com/gsnedders/python-webencodings) | BSD-3-Clause |
| brotli | 1.2.1 | [google/brotli](https://github.com/google/brotli) | MIT |
| zopfli | 0.4.3 | [google/zopfli](https://github.com/google/zopfli) | Apache-2.0 |

## Source provenance: current status

<badge>PARTIALLY COMPLIANT — NOT GITHUB-ONLY</badge>

- The new story, character, SVG illustration, EPUB and static-site agents use Python's standard library only.
- The quality and artwork-only workflows use GitHub-hosted runners and GitHub Actions; they do not install Python packages.
- The print workflow currently resolves the pinned Python packages through pip's default package index. The existence of upstream GitHub repositories does **not** mean the workflow fetched those source archives from GitHub.
- Native libraries, fonts, qpdf and Poppler are installed from Ubuntu package repositories with apt. Those are not GitHub-only sources.
- The lock pins package versions but does not yet pin artifact hashes or prove GitHub-origin downloads.
- GitHub Actions are currently referenced by version tags; full commit-SHA pinning remains pending.

## Required work before claiming strict GitHub-only sourcing

1. Decide whether the immutable `ubuntu-24.04` runner image is an allowed platform baseline. If not, every native library and font needs a GitHub-origin build/source plan.
2. Vendor or fetch each Python source distribution from its verified upstream GitHub repository at an immutable commit/tag; verify checksums and licenses.
3. Audit Pyphen dictionary licensing and retain all required notices.
4. Pin each third-party Action to a reviewed full commit SHA.
5. Produce an SBOM and provenance report from the actual build, not just this manually maintained table.
6. Re-run the full PDF/EPUB/site workflow using only the approved GitHub-origin inputs.

Do not describe the current print workflow as fully GitHub-only until these steps pass. No paid API, hosted model endpoint, external server, or model weights are used by the current pipeline.
