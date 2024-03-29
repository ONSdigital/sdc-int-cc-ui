# syntax=docker/dockerfile:1
FROM python:3.9-alpine
WORKDIR /
ENV FLASK_APP=application.py
ENV FLASK_ENV=development
ENV SECRET_KEY=secretkeysetasenvva
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers libxml2-dev xmlsec xmlsec-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
RUN pip install -e .
CMD ["flask","run","--no-reload"]
