build:
	docker build -t cotainr-dev .

shell:
	docker run --name cotainr-dev --rm -i -t cotainr-dev bash

tests:
	docker run --privileged -t cotainr-dev python3 -m pytest -vv

unittests:
	docker run -t cotainr-dev python3 -m pytest -vv -m "not endtoend and not singularity_integration and not conda_integration"
