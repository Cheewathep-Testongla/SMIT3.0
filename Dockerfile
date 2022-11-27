# Dockerfile
FROM python:3.10

ENV LISTEN_PORT=443

RUN mkdir /SMIT3.0
WORKDIR /SMIT3.0

RUN pip install --upgrade pip
RUN pip install fastapi uvicorn

RUN apt-get update \ 
    &&  apt-get install -y apt-transport-https \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17
   
RUN ACCEPT_EULA=Y apt-get install mssql-tools unixodbc-dev

COPY . .

RUN pip install -r python_lib.txt

EXPOSE 443

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "443"]
# 
# CMD ["unicorn", "-w", "12","-k", "uvicorn.workers.UvicornWorker","-t","0", "wsgi:app", "--bind", "0.0.0.0:80"]