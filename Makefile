build:
	docker build -t ghcr.io/airyhq/rasa-x-demo/rasa:latest .

release: build
	docker push ghcr.io/airyhq/rasa-x-demo/rasa:latest
