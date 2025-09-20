FROM python:3.11-slim

WORKDIR /workspace

RUN apt-get update \
  && apt-get install -y git build-essential curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# create a user to avoid running as root
RUN useradd -m dev && chown -R dev:dev /workspace
USER dev

EXPOSE 8888
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--allow-root", "--NotebookApp.token=''"]
