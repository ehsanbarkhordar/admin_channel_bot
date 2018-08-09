#Download base image python 3.5
FROM python:3.5
RUN echo "Asia/Tehran" > /etc/timezone

WORKDIR /admin_channel

COPY ./requirements.txt /admin_channel/requirements.txt

RUN pip install -r requirements.txt

COPY ./ /admin_channel

CMD ["python3.5", "bot.py"]

