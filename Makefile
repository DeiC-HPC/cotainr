build:
	@docker build  -t test .

build-nocache:
	@docker build --no-cache -t test .

shell:
	@docker run --name container-main --rm -i -t test bash

tests:
	@docker run --name container-test --rm -t test python3 -m pytest cotainr/tests/cli