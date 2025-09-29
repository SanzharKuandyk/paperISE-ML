FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential clang clang-format git python3 python3-pip python3-venv \
    gcc make curl wget file pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir pandas scikit-learn numpy joblib

# Optional tools (KLEE, AFL, kcov) are NOT installed by default in this Dockerfile.
# Installing KLEE or AFL usually requires additional build steps and packages.

WORKDIR /workspace
CMD ["/bin/bash"]
