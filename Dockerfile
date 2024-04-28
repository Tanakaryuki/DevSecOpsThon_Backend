# python3.11のイメージをダウンロード
FROM nvcr.io/nvidia/pytorch:24.03-py3
ENV PYTHONUNBUFFERED=1

WORKDIR /src

COPY requirements.txt ./
RUN pip install -r requirements.txt

ENTRYPOINT ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--reload"]
