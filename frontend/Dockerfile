FROM python:3.10

WORKDIR /usr/src/app

COPY ./requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["streamlit", "run", "main.py", "--server.port", "49551"]
