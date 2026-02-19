FROM us.gcr.io/google.com/cloudsdktool/google-cloud-cli:alpine

RUN gcloud components install kubectl -q --no-user-output-enabled

# Install Helm
RUN mkdir helm_tmp \
  && curl -fsSL -o helm_tmp/helm.tar.gz https://get.helm.sh/helm-v4.1.1-linux-amd64.tar.gz \
  && curl -fsSL -o helm_tmp/helm.tar.gz.sha256 https://get.helm.sh/helm-v4.1.1-linux-amd64.tar.gz.sha256 \
  && (cd helm_tmp && sha256sum -c helm.tar.gz.sha256) \
  && tar -zxvf helm_tmp/helm.tar.gz -C helm_tmp \
  && mv helm_tmp/linux-amd64/helm /bin/helm \
  && rm -rf helm_tmp
