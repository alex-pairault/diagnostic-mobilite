init-pip:
	pip install -r requirements.txt

init-poetry:
	poetry install

style:
	poetry run pre-commit run -a
