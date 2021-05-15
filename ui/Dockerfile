# Multistage build for JS artifacts
FROM gcr.io/flipperkid-default/chalk-ui-base:latest as js_app
WORKDIR /js

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

# Copy over nginx configuration
RUN rm -f /etc/nginx/conf.d/*
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf
COPY conf.d/app.conf /etc/nginx/conf-includes/app.conf

# Copy over built JS files from React app
COPY --from=js_app /js/web-build/* /www/client/

CMD ["nginx", "-g", "daemon off;"]
