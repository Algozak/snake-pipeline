# snake-pipeline

Snake game API (FastAPI + PostgreSQL) used as a hands-on DevOps learning project.
The application is intentionally small. The point of the repository is the
infrastructure around it, which is built step by step and tracked in the git history.

> The application code was generated with AI assistance and reviewed by me.
> The Docker, CI/CD and infrastructure parts are written by me as part of my DevOps learning path.

## What it does

- Register and log in (passwords are hashed)
- Submit a score and get the top-10 table
- `GET /health` endpoint for health checks
- Plain HTML/JS Snake game in `frontend/`

## Project structure

```
backend/     FastAPI application (+ Dockerfile)
frontend/    static page with the game
sql/         database schema
tests/       pytest tests
```

## Run without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in your own values, never commit .env
uvicorn backend.main:app --port 6500
```

Run the tests:

```bash
pytest
```

## Run the backend in Docker

The build context is the repository root:

```bash
docker build -f backend/Dockerfile -t snake-pipeline:v1 .
docker run --rm -p 127.0.0.1:6500:6500 --env-file .env snake-pipeline:v1
```

The port is published on `127.0.0.1` only, so it is not reachable from the network.

## Roadmap

- [x] Application: backend, schema, tests
- [x] Native Docker image for the backend (basic Dockerfile)
- [x] Optimized Dockerfile: layer cache, `.dockerignore`, non-root user
- [ ] Multi-stage build
- [ ] Docker Compose: nginx + backend + PostgreSQL, healthchecks, named volume
- [ ] Resource limits, secrets handling, hardening
- [ ] PostgreSQL backup and restore
- [ ] Images in GHCR with versioned tags
- [ ] CI with GitHub Actions: tests, lint, image build, security scan
- [ ] Deploy to a Debian server with Ansible, rollback
- [ ] Monitoring and logging

## Status

Work in progress. Milestones are marked with git tags, see the Releases / Tags page.

## License

MIT