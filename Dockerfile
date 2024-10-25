FROM python:3.10-alpine

WORKDIR /boilr_app
COPY . .

RUN mkdir -p /var/log/boilr
RUN mkdir -p /etc/boilr

RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3", "-m" , "boilr", "-v", "run"]
