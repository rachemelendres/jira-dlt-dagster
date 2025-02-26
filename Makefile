.PHONY: build-dagster dagster duckdb clean

# Build Docker image for Dagster
build-dagster:
	docker compose build dagster

# Start the Dagster service
dagster:
	docker compose up dagster

# Run the DuckDB CLI
duckdb:
	docker compose run --rm duckdb

# Remove Docker containers, networks, volumes, and images created by up
clean:
	docker compose down --rmi all --volumes --remove-orphans
