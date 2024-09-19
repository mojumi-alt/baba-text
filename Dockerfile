FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./baba_text ./baba_text
COPY ./resources ./resources
COPY ./bot.py .

CMD [ "python", "./bot.py" ]
