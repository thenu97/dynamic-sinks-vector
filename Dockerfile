FROM python:3.12-slim
RUN pip install poetry
WORKDIR /app
ADD . .
RUN poetry build

FROM python:3.12-slim
COPY --from=0 /app/dist/*.whl /
RUN pip install dynamic_sinks_vector-*-py3-none-any.whl

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "dynamic-sinks-vector.main"]
