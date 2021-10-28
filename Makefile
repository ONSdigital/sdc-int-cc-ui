DESIGN_SYSTEM_VERSION=`cat .design-system-version`

clean:
	rm -rf templates/components
	rm -rf templates/layout

load-design-system-templates:
	./scripts/load_templates.sh $(DESIGN_SYSTEM_VERSION)

build: load-design-system-templates

link-development-env:
	ln -sf .development.env .env

run: build link-development-env
	pipenv run flask run