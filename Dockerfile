FROM python:3.7

# Create app directory
WORKDIR /usr/src/app

# copy over the files
COPY . .

# install deps and compile
RUN pip install pipenv
RUN pipenv install --system --deploy

EXPOSE 8050

CMD gunicorn -w 4 -b 0.0.0.0:8050 --max-requests 20 application:server

CMD [ "python", "index.py"  ]
