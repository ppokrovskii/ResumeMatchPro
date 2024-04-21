set %PYTHONPATH%=%PYTHONPATH%;%CD%\alembic
cd ./alembic/
alembic upgrade head
