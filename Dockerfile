FROM python:3.7.5-slim-stretch

ARG UID=1002
ARG GID=1001

RUN groupadd -g $GID celery && \
    useradd -m -u $UID -g $GID --shell /bin/bash celery

## RUBY
RUN apt-get update && \
    apt-get install -y git ruby ruby-dev ruby-bundler build-essential curl && \
    rm -rf /var/lib/apt/lists/*

RUN gem install bibliothecary curl

WORKDIR /

COPY requirements.txt .

### Install python dependencies
RUN pip install -r requirements.txt

WORKDIR /home/celery/opencelery

RUN chown -R celery:celery /home/celery/opencelery/

USER celery
# Copy all
COPY . .

CMD /bin/bash
