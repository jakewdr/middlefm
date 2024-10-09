FROM python:3.11.10-alpine3.20

ADD main.py .
ADD secrets.json .
ADD automaticEdits.json .
ADD requirements.txt .
ADD .cache .

RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]