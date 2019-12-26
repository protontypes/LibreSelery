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

USER proton

WORKDIR /home/proton

# Copy all
COPY . .

<<<<<<< HEAD
CMD /bin/bash
=======
ENTRYPOINT ["python","/home/proton/proton.py"]
CMD []
>>>>>>> 84c046ec47ebd74aa60226e5cc5c47754907cd5d
