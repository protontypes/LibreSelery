FROM python:3.7.5-slim-stretch

ARG UID=1001
ARG GID=1002

########### D E P S  ###########
RUN groupadd -g $GID selery && \
    useradd -m -u $UID -g $GID --shell /bin/bash selery

## RUBY
RUN apt-get update && \
    apt-get install -y git ruby ruby-dev ruby-bundler build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /

COPY Gemfile .

RUN bundle install

########### P R E P ###########
### Copy openselery into the image for installation
COPY . /home/selery/openselery/
### create other useful dirs
RUN mkdir -p /home/selery/results

WORKDIR /home/selery/openselery


### permissions so someone can reinstall openselery from inside the container
RUN chown -R selery:selery /usr/local/lib/python3.7/site-packages/
RUN chown -R selery:selery /usr/local/bin
### prepare selery user permissions
RUN chown -R selery:selery /home/selery/openselery
RUN chown -R selery:selery /home/selery/results

### change user
USER selery


########### I N S T A L L ###########
### Install openselery and it's dependencies
RUN python setup.py install


########### P O S T ###########
### set image entrypoint to be openselery executable
ENTRYPOINT ["selery", "run"]
