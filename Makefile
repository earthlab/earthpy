docs: docs/*.rst docs/conf.py docs/Makefile earthpy/*.py *.rst ## generate html docs
	rm -f docs/earthpy.rst
	rm -f docs/modules.rst
	sphinx-apidoc -H "API reference" -o docs/ earthpy earthpy/tests earthpy/example-data
	$(MAKE) -C docs clean
	$(MAKE) -C docs doctest
	$(MAKE) -C docs html
	$(MAKE) -C docs linkcheck
