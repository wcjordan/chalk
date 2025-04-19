FROM gcr.io/google.com/cloudsdktool/google-cloud-cli:alpine

RUN gcloud components install kubectl -q --no-user-output-enabled

# Install Helm
RUN mkdir helm_tmp \
  && curl -o helm_tmp/helm.tar.gz https://get.helm.sh/helm-v3.17.1-linux-amd64.tar.gz \
  && tar -zxvf helm_tmp/helm.tar.gz -C helm_tmp \
  && mv helm_tmp/linux-amd64/helm /bin/helm \
  && rm -rf helm_tmp
