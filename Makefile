build:
	docker build -t test .

shell:
	docker run --name container-main --rm -i -t test bash

tests:
	docker run --privileged -t test python3 -m pytest -vv

unittests:
	docker run -t test python3 -m pytest -vv -m "not endtoend and not singularity_integration and not conda_integration"
