FROM us.gcr.io/google.com/cloudsdktool/google-cloud-cli:alpine

RUN gcloud components install kubectl -q --no-user-output-enabled

# Install Helm
RUN mkdir helm_tmp \
  && curl -fsSL -o helm_tmp/helm.tar.gz https://get.helm.sh/helm-v4.1.4-linux-amd64.tar.gz \
  && curl -fsSL -o helm_tmp/helm.tar.gz.sha256 https://get.helm.sh/helm-v4.1.4-linux-amd64.tar.gz.sha256 \
  && cd helm_tmp \
  && echo "$(head -n 1 helm.tar.gz.sha256) helm.tar.gz" > helm.tar.gz.sha256 \
  && sha256sum -c helm.tar.gz.sha256 \
  && tar -zxvf helm.tar.gz -C . \
  && mv linux-amd64/helm /bin/helm \
  && cd .. \
  && rm -rf helm_tmp
