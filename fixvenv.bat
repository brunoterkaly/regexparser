call venv/scripts/deactivate
rd venv /s
call python -m venv venv
call venv/scripts/activate
call pip install -r requirements.txt
