
# Use different image for runtime
FROM python:3.7-slim AS cluster_dict_serve:v1

WORKDIR /home/appuser

COPY cluster_dict /home/appuser/cluster_dict
COPY setup.py .
COPY requirements.txt .

RUN pip install -r requirements.txt && python setup.py install

# Create non-root user (Security First!)
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# CMD [ "python3 -m cluster_dict serve" ]