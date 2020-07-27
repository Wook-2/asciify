FROM python:3.6-slim

RUN pip install flask
RUN pip install flask_limiter
RUN pip install pillow
RUN pip install image
RUN pip install numpy
COPY . .

EXPOSE 8080

CMD python3 server.py
