runserver:
	uvicorn main:app --reload

migrations:
	alembic revision --autogenerate -m "$(name)"

migrate:
	alembic upgrade head

reverse-migrate:
	alembic downgrade -$(q)

ruff:
	ruff format .