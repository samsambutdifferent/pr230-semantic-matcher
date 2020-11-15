FROM python:3.7-slim
WORKDIR /app
ADD . /app
ADD ./requirements.txt /app

#Set env vars
ENV GOOGLE_APPLICATION_CREDENTIALS "./key.json"

# Install any necessary dependencies
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn
RUN python -m spacy download en_core_web_lg

CMD exec gunicorn --bind :8080 --workers 1 --threads 1 --timeout 0 app:app