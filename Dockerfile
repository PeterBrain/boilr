FROM python:3.9-alpine

COPY . .

RUN mkdir -p /var/log/boilr
RUN touch /var/log/boilr/boilr.log

WORKDIR /

RUN pip3 install -r requirements.txt

CMD [ "python3", "-m" , "boilr", "-v", "debug"]
