FROM node:8.11.2
MAINTAINER Daniel Marchena <danielmapar@gmail.com>

# Expose the default port
EXPOSE 8080

# Create/Set the working directory
RUN mkdir /app
WORKDIR /app

COPY package.json /app/package.json
RUN npm install && npm install -g sequelize-cli

# Copy App
COPY . /app

#RUN chmod 777 ./wait-for-it.sh && ./wait-for-it.sh db:3306

#RUN npm install -g sequelize-cli && sequelize db:migrate

# Set Entrypoint
ENTRYPOINT chmod 777 ./wait-for-it.sh && ./wait-for-it.sh -t 40 db:3306 && sequelize db:migrate && npm run start
