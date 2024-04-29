FROM python:3.10

WORKDIR /usr/src/app

COPY ./requirements.txt ./
COPY ./main.py ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["streamlit", "run", "main.py", "--server.port", "49550"]
