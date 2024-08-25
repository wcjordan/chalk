# Multistage build for JS artifacts
FROM node:20 AS base
WORKDIR /workspace/js

ENV ENVIRONMENT=prod
ENV DEBUG=false
ARG sentryDsn
ENV SENTRY_DSN=$sentryDsn

# Install system packages for dev tooling
RUN apt-get update && apt-get install -y \
  bash \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

# Install sharp-cli for expo / metro bundler
RUN npm install -g sharp-cli@^2.1.0

# Install React dependencies
COPY js/yarn.lock js/package.json js/.yarnrc.yml ./
COPY js/.yarn/ ./.yarn/
RUN corepack enable && yarn install --immutable && yarn cache clean

# Multistage - test container
FROM base AS js_test_env
RUN npx playwright install && npx playwright install-deps

# Build storybook for testing
COPY js/babel.config.js js/App.tsx ./
COPY js/.storybook/ ./.storybook/
COPY js/assets/ ./assets/
COPY js/__mocks__/ ./__mocks__/
COPY js/src/ ./src/
RUN npx storybook build --test --quiet
WORKDIR /workspace

# Multistage - built app
FROM base AS js_app_build

# Install React app
COPY js/.prettierrc js/.eslintrc js/tsconfig.json js/app.config.js js/babel.config.js js/App.tsx ./
COPY js/.storybook/ ./.storybook/
COPY js/assets/ ./assets/
COPY js/src/ ./src/

# Build React app
RUN yarn build

# Multistage - nginx container
FROM nginx:alpine AS js_app_prod

# Copy over built JS files from React app
COPY --from=js_app_build /workspace/js/dist/ /www/client/

CMD ["nginx", "-g", "daemon off;"]
