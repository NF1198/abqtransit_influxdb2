FROM alpine
WORKDIR /code
RUN apk add --no-cache tzdata gcc python3 py3-pip py3-wheel musl-dev linux-headers python3-dev
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:5000", "--workers=3", "app:app" ]