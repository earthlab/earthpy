docs: ## generate Sphinx HTML documentation, including API docs
		rm -f docs/earthpy.rst
		rm -f docs/modules.rst
		sphinx-apidoc -H "API reference" -o docs/ earthpy earthpy/tests earthpy/example-data
		$(MAKE) -C docs clean
		$(MAKE) -C docs doctest
		$(MAKE) -C docs html
		$(MAKE) -C docs linkcheck
