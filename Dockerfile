FROM ruby:3.3-slim
RUN apt-get update && apt-get install -y build-essential git && rm -rf /var/lib/apt/lists/*
WORKDIR /srv/jekyll
COPY Gemfile Gemfile.lock ./
RUN bundle install
