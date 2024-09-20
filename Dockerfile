FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./baba_text ./baba_text
COPY ./resources ./resources
COPY ./bot.py .

# Health check for ECS, do not remove!
HEALTHCHECK --interval=2s --timeout=1s CMD exit 0

CMD [ "python", "./bot.py" ]
