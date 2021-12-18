# Multistage build for JS artifacts
ARG GCP_PROJECT
FROM gcr.io/${GCP_PROJECT}/chalk-ui-base:latest as js_app
WORKDIR /js

ENV ENVIRONMENT=prod
ENV DEBUG=false
ARG expoClientId
ENV EXPO_CLIENT_ID=$expoClientId
ARG sentryDsn
ENV SENTRY_DSN=$sentryDsn

# Install React dependencies
COPY js/yarn.lock .
COPY js/package.json .
RUN yarn install --pure-lockfile && yarn cache clean

# Install React app
COPY js/.prettierrc .
COPY js/.eslintrc .
COPY js/tsconfig.json .
COPY js/.storybook ./.storybook

COPY js/web ./web
COPY js/app.config.js ./app.config.js
COPY js/App.tsx ./App.tsx
COPY js/assets ./assets
COPY js/src ./src

# Build React app
RUN yarn build

# Multistage - nginx container
FROM nginx:alpine

# Copy over built JS files from React app
COPY --from=js_app /js/web-build/ /www/client/

CMD ["nginx", "-g", "daemon off;"]
