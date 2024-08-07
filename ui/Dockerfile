# Multistage build for JS artifacts
FROM node:20 AS base
WORKDIR /js

ENV ENVIRONMENT=prod
ENV DEBUG=false
ARG sentryDsn
ENV SENTRY_DSN=$sentryDsn

# Install system packages for dev tooling
RUN apt-get update && apt-get install -y \
  bash \
  build-essential \
  && rm -rf /var/lib/apt/lists/*
RUN npm install -g sharp-cli

# Install React dependencies
COPY js/yarn.lock .
COPY js/package.json .
RUN yarn --silent install --immutable && yarn cache clean

# Multistage - built app
FROM base AS js_app

# Install React app
COPY js/.prettierrc .
COPY js/.eslintrc .
COPY js/tsconfig.json .
COPY js/.storybook ./.storybook

COPY js/app.config.js ./app.config.js
COPY js/babel.config.js ./babel.config.js
COPY js/App.tsx ./App.tsx
COPY js/assets ./assets
COPY js/src ./src

# Build React app
RUN yarn build

# Multistage - nginx container
FROM nginx:alpine

# Copy over built JS files from React app
COPY --from=js_app /js/dist/ /www/client/

CMD ["nginx", "-g", "daemon off;"]
