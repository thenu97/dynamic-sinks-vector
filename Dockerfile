FROM python:3.12-slim
RUN pip install poetry==1.2.0a2
WORKDIR /app
ADD . .
RUN poetry build

FROM python:3.12-slim
COPY --from=0 /app/dist/*.whl /
RUN pip install dynamic-sinks-vector-*.*.*-py3-none-any.whl

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "dynamic-sinks-vector.main"]
