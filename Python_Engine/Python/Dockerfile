# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:latest AS uv
FROM mcr.microsoft.com/dotnet/aspnet:10.0-bookworm-slim AS dotnet

FROM python:3.10-slim-bookworm

COPY --from=uv /uv /opt/BHoM/Extensions/Python/tools/uv
COPY --from=dotnet /usr/share/dotnet /usr/share/dotnet

ENV DOTNET_ROOT=/usr/share/dotnet \
    PYTHONNET_RUNTIME=coreclr \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PATH="/opt/BHoM/Extensions/Python/Python_Toolkit/.venv/bin:/opt/BHoM/Extensions/Python/tools:/usr/share/dotnet:${PATH}" \
    PYTHONPATH="/opt/BHoM/Assemblies"

WORKDIR /opt/BHoM/Extensions/Python/Python_Toolkit

# Requires the bhom-assemblies named build context.
COPY --from=bhom-assemblies . /opt/BHoM/Assemblies

COPY pyproject.toml README.md ./
COPY src ./src

RUN /opt/BHoM/Extensions/Python/tools/uv sync --no-dev --no-editable
