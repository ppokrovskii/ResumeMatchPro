## run docker compose

```bash
docker-compose up
```

## run docker compose with build

```bash
docker-compose up --build
```

## create alembic revision

```bash
alembic revision --autogenerate -m "message"
```

## upgrade database

```bash
alembic upgrade head
```