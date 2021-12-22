FROM python:3.9

WORKDIR /code

COPY requirements.txt /code
RUN pip install --upgrade pip && pip install -r /code/requirements.txt
COPY . /code

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
