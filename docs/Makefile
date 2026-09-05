SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = text
BUILDDIR      = _build
APIDIR        = $(SOURCEDIR)/api

.PHONY: help clean api html linkcheck github
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
clean:
	rm -rf "$(BUILDDIR)" "$(APIDIR)"
api:
	rm -rf "$(APIDIR)"
	mkdir -p "$(APIDIR)"
	sphinx-apidoc --private -e -f -o "$(APIDIR)" ../src/pofff
html: api
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
linkcheck: api
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
github: html
	cp -a "$(BUILDDIR)/html/." .
