FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

WORKDIR /opt/dagster/app

ENV UV_PROJECT_ENVIRONMENT=/usr/local

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /opt/dagster/app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Expose the port for the Dagster development server
EXPOSE 3000

# Set the entrypoint to run the Dagster development server
ENTRYPOINT ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]