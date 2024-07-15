.PHONY: init setup run streamlit docker-up docker-down docker-clean docker-stop docker-restart docker-logs docker-exec

init:
	`which python3.11` -m venv venv
	venv/bin/pip install pip==23.2.1 pip-tools wheel --no-cache-dir
	venv/bin/pip-compile -o requirements.txt --no-header --no-emit-index-url --no-emit-trusted-host requirements.in
	venv/bin/pip-compile -o requirements-dev.txt --no-header --no-emit-index-url --no-emit-trusted-host requirements-dev.in

setup: requirements-dev.txt
	venv/bin/pip-sync requirements-dev.txt
	venv/bin/pre-commit install
	`which python3.11` -m nltk.downloader stopwords
	mkdir -p ${PWD}/dagster_home
	touch ${PWD}/dagster_home/dagster.yaml

lint:
	venv/bin/pre-commit run --all-files

run: dagster_home
	export DAGSTER_HOME=${PWD}/dagster_home && \
	venv/bin/dagster-webserver -h 0.0.0.0 -p 3000

streamlit:
	venv/bin/streamlit run src/streamlit/hello.py

docker-up:
	docker compose --file docker-compose.yml up --detach --build

docker-down:
	docker compose --file docker-compose.yml down

docker-clean:
	docker compose --file docker-compose.yml down --volumes --remove-orphans

docker-stop:
	docker compose --file docker-compose.yml stop

docker-restart:
	docker compose --file docker-compose.yml restart

docker-logs:
	docker compose --file docker-compose.yml logs --follow

docker-exec:
	docker compose --file docker-compose.yml exec $(ARGS)
