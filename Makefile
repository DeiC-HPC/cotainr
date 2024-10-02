build:
	docker build -t test .

shell:
	docker run --name container-main --rm -i -t test bash

tests:
	docker run -t test python3 -m pytest cotainr/tests/cli
