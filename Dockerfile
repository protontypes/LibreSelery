FROM python:3.7.5-slim-stretch

ARG UID=1001
ARG GID=1002

RUN groupadd -g $GID selery && \
    useradd -m -u $UID -g $GID --shell /bin/bash selery

## RUBY
RUN apt-get update && \
    apt-get install -y git ruby ruby-dev ruby-bundler build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /

COPY Gemfile .

RUN bundle install

COPY requirements.txt .

### Install python dependencies
RUN pip install -r requirements.txt

WORKDIR /home/selery/runningrepo

RUN chown -R selery:selery /home/selery/runningrepo

USER selery
# Copy all
COPY . .

CMD /bin/bash
