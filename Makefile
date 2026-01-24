# like "scripts" section in package.json

# To start everything: make dev
# To run migrations: make migrate
# To trigger the ingestion: make ingest
# To stop background tasks: make stop

install:
	pip install -r requirements.txt

migrate:
	python manage.py makemigrations
	python manage.py migrate

# Like "npm run dev"
# This starts redis, then runs django and celery together
dev: stop
	sudo service redis-server start
	./venv/bin/python manage.py runserver --noreload & ./venv/bin/celery -A core worker --loglevel=info

# to stop everything
stop:
	# Kill process on port 8000
	sudo fuser -k 8000/tcp || true
	# Use [c] and [m] trick to prevent pkill from killing the make command itself
	pkill -9 -f "[c]elery worker" || true
	pkill -9 -f "[m]anage.py runserver" || true

ingest:
	python manage.py shell -c "from api.tasks import ingest_customer_data, ingest_loan_data; ingest_customer_data.delay('customer_data.xlsx'); ingest_loan_data.delay('loan_data.xlsx')"


docker-prepare:
	pip freeze > requirements.txt
	docker-compose up --build