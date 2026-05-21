test:
	python -m unittest discover -s tests -p 'test_*.py'

load-config:
	python -m brek load-config
