FROM node:alpine

WORKDIR /app

COPY package*.json .

RUN apk add --no-cache curl && npm install

COPY . .

CMD ["npm", "run", "start"]
