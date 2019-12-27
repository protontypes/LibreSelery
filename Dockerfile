FROM python:3.7.5-slim-stretch

ARG UID=1002
ARG GID=1001

RUN groupadd -g $GID proton && \
    useradd -m -u $UID -g $GID --shell /bin/bash proton

## RUBY
RUN apt-get update && \
    apt-get install -y git ruby ruby-dev ruby-bundler build-essential curl && \
    rm -rf /var/lib/apt/lists/*

RUN gem install bibliothecary curl

WORKDIR /

COPY requirements.txt .

### Install python dependencies
RUN pip install -r requirements.txt

WORKDIR /home/proton/protontypes

USER proton
# Copy all
COPY . .

# Create folder for dotfiles Dotfiles
RUN mkdir /home/proton/.protontypes

CMD /bin/bash
