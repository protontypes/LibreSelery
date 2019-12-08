FROM python:3.7.5-slim-stretch

WORKDIR /root

### Install python dependencies
COPY requirements.txt . 

RUN pip install -r requirements.txt

### RUBY
RUN apt-get update && \
    apt-get install -y ruby ruby-dev ruby-bundler build-essential curl && \
    rm -rf /var/lib/apt/lists/*

RUN gem install bibliothecary curl

CMD ["bash"]