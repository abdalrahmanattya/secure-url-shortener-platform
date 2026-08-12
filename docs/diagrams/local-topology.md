# Local topology

Status: locally verified as a Compose design; end-to-end execution evidence is
recorded separately.

```mermaid
flowchart LR
    C[Browser or curl] -->|HTTP :8000| A[FastAPI app container]
    A -->|SQLAlchemy async session| D[(PostgreSQL 16 container)]
    A --> L[Request log and process metrics]
    A --> V[Static UI and templates]
    M[Compose migrate service\nalembic upgrade head] --> D
    D --> Q[Disposable named volume]
```

The local database values are deterministic demo values only. The application
container runs as a non-root user; cloud credentials are not required.
