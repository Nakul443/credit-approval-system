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
dev:
	# This starts redis, then runs django and celery together
	sudo service redis-server start
	python manage.py runserver & ./venv/bin/celery -A core worker --loglevel=info

# To stop everything
stop:
	pkill -f "runserver"
	pkill -f "celery"

ingest:
	python manage.py shell -c "from api.tasks import ingest_customer_data, ingest_loan_data; ingest_customer_data.delay('customer_data.xlsx'); ingest_loan_data.delay('loan_data.xlsx')"