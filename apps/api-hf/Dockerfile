FROM python:3.12-slim

# Install build tools as root BEFORE switching user
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
ENV HF_HOME=/tmp/hf-cache
ENV TRANSFORMERS_CACHE=/tmp/hf-cache
ENV TORCH_HOME=/tmp/torch-cache
ENV XDG_CACHE_HOME=/tmp/cache
ENV TOKENIZERS_PARALLELISM=false

WORKDIR /app
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY --chown=user . /app

EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
