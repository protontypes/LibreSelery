FROM python:3.7.5-slim-stretch

WORKDIR /root

COPY requirements.txt .

### RUBY
RUN apt-get update && \
    apt-get install -y ruby ruby-dev ruby-bundler build-essential curl && \
    rm -rf /var/lib/apt/lists/*

RUN gem install bibliothecary curl

# Copy all
COPY . .

### Install python dependencies
RUN pip install -r requirements.txt

CMD ["bash"]
