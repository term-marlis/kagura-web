FROM python:3.5.1

MAINTAINER yuto.matsuki@recochoku.co.jp

ADD peach-swagger-client /lib/peach-swagger-client
ADD peach-web /app
WORKDIR /app/

RUN pip install -e /lib/peach-swagger-client
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "manage.py", "runserver", "--host", "0.0.0.0"]
