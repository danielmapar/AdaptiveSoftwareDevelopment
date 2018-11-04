FROM node:8.11.2
MAINTAINER Daniel Marchena <danielmapar@gmail.com>

# Create/Set the working directory
RUN mkdir /app
WORKDIR /app

COPY package.json /app/package.json
RUN npm install

# Copy App
COPY . /app

# Set Entrypoint
ENTRYPOINT npm run start
