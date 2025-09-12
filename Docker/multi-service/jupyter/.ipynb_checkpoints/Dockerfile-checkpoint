FROM python:3.10-slim
WORKDIR /home/jovyan/work

# Install JupyterLab directly
RUN pip install --no-cache-dir jupyterlab

EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--ServerApp.token="]
