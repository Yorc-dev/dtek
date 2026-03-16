FROM python:3.12.2-slim

WORKDIR /backend
RUN touch ../__init__.py

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/backend"

RUN apt-get update && apt-get install -y libreoffice libreoffice-writer

RUN apt install gettext -y
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .


EXPOSE 8000
