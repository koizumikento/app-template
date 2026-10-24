# Backend

## Dependency security updates

From this directory, install the committed lock and run the full backend checks:

```sh
uv sync --locked --dev
uv run --frozen pytest -v
uv run --frozen ruff check .
uv run --frozen ruff format --check .
```

The lock and uv constraint require `certifi>=2026.10.19` for the
[emSign CA incident](https://github.com/certifi/python-certifi/security/advisories/GHSA-6q48-6c7w-9gw2).
For a targeted future update, run `uv lock --upgrade-package certifi`, inspect the
diff, and rerun the checks. Docker uses `uv sync --frozen`, so changing only an
installed environment does not update subsequent builds.

## Runtime and image maintenance

The builder (`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`) and runtime
(`python:3.12-slim-bookworm`) tags float independently. `uv.lock` fixes application
dependencies, not Python, uv, OS packages, or their CA stores. For reproducible
release builds, select and test compatible Python 3.12 patch versions in both
stages, pin the verified images by digest, and record the Python/uv versions and
resolved digests. Review and refresh these pins regularly to receive security
fixes; a digest pin alone does not establish that an image is patched. The
Dockerfile's apt repositories also change over time, so image pins alone do not
make the complete build reproducible.

With Docker running, validate a fresh local build from the repository root:

```sh
docker build --pull --no-cache -t app-template-backend:security-check ./backend
```

Inspect the resulting image's Python/uv (builder), pip (if present), and Debian
`ca-certificates` versions against upstream advisories. Rebuild API and worker
images after updates; running containers and existing virtual environments retain
their old contents. Updating application certifi does not update pip's vendored
certifi, uv's trust configuration, or the OS trust store. Review/update those
separately following the
[Python release guidance](https://blog.python.org/2026/10/python-3151-3149-31317/).
Keep TLS verification enabled.

As of 2026-10-24, the October 21 Python releases do not establish a stable fix for
the October 22 `tar_filter` patch (CVE-2026-114583). No direct tar extraction path
was found in this backend. Track upstream Python/distribution fixes and verify
the selected image's patch status before release; this dependency update does
not resolve that runtime risk.
