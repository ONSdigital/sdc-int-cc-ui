clean:
	rm -rf templates/components
	rm -rf templates/layout

load-design-system-templates:
	./scripts/load_templates.sh

build: load-design-system-templates

link-development-env:
	ln -sf .development.env .env

run: build link-development-env
	pipenv run flask run --port 5001

test: link-development-env
	pipenv run pytest tests

flake8:
	pipenv run flake8
