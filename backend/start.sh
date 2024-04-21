#!/bin/bash
# add source roots to pythonpath
export PYTHONPATH=$PYTHONPATH:$(pwd)/application
# add content of alembic.ini to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/alembic
# add application to PYTHONPATH
#export PYTHONPATH=$PYTHONPATH:$(pwd)

# run alembic and uvicorn then
cd alembic/
alembic upgrade head
cd ../application/
uvicorn main:app --host 0.0.0.0
