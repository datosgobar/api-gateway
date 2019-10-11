.PHONY: docs servedocs doctoc

clean:
	rm -rf venv/
	cat /dev/null | crontab

SHELL = bash

servedocs:
	mkdocs serve -a localhost:8080

mkdocsdocs:
	mkdocs build
	rsync -vau --remove-source-files site/ docs/
	rm -rf site

docs: mkdocsdocs

doctoc: ## generate table of contents, doctoc command line tool required
        ## https://github.com/thlorenz/doctoc
	doctoc --maxlevel 4 --github --title "## Indice" docs/
	find docs/ -name "*.md" -exec bash fix_github_links.sh {} \;

pdf:
	mkdocs_datosgobar md2pdf mkdocs.yml docs/monitoreo-apertura-docs.pdf
