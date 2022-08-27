FROM python:3.10.6

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "main.py"]
# Or enter the name of your unique directory and parameter set.