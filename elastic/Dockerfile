FROM python:3.7-alpine

RUN pip install elasticsearch elasticsearch_dsl

COPY ./ /app/

WORKDIR /app

CMD ["python", "loader.py"]
