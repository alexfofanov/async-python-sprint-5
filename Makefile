all: start

start:
	docker-compose up --build -d

stop:
	docker-compose down

test:
	docker-compose exec file-storage-api pytest -v tests
