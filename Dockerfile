FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/baba_text ./baba_text
COPY ./tests ./tests
COPY ./bot.py .

CMD [ "python", "-m", "unittest", "discover", "tests" ]
