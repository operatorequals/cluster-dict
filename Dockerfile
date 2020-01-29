
# Use different image for runtime
FROM python:3.7-slim AS cluster_dict_serve:v1

# Create non-root user (Security First!)
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY cluster_dict /home/appuser

CMD [ "python3 -m cluster_dict serve" ]