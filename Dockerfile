###########################################
# dev
###########################################

ARG BASE_IMAGE=python:3.9.8-slim-buster

FROM "${BASE_IMAGE}" 

# upgrade pip
RUN pip install --upgrade pip
RUN apt-get update -yqq

# Install the python package managers.
RUN pip install -U \
    pip \
    setuptools \
    wheel \
    poetry

ENV FLASK_HOME=/home/app

RUN mkdir ${FLASK_HOME}

RUN mkdir -p /var/log/web && touch /var/log/web/web.err.log && touch /var/log/web/web.out.log



WORKDIR ${FLASK_HOME}
COPY /clone_status ./
COPY .env ../
COPY pyproject.toml ${FLASK_HOME}
COPY poetry.lock $FLASK_HOME

RUN poetry export --without-hashes -f requirements.txt --output requirements.txt
ENV PYTHONPATH=${PYTHONPATH}:${PWD} 

RUN export FLASK_APP=app.py

RUN pip install -r requirements.txt

EXPOSE 5000

# Using a "heredoc" called `dev_command.sh` because this is the only place and time this script will be needed
RUN echo "poetry install" >> ${FLASK_HOME}/dev_command.sh
RUN echo "poetry run python3 app.py" >> ${FLASK_HOME}/dev_command.sh
RUN chmod +x ${FLASK_HOME}/dev_command.sh

EXPOSE 3000
CMD ["bash", "dev_command.sh"]


# CMD ["python", "app.py"]

# CMD ["bash", "-c", "while true; do sleep 1; done"]
