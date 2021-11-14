FROM python:3
WORKDIR /usr/src/app
COPY ./python_code/requirements.txt ./requirements.txt
RUN python3 -m pip install -r requirements.txt