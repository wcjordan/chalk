/**
 * Helper to login to Google Artifact Registry and configure Docker to use it.
 */
def login(registryHost) {
    withCredentials([
        file(credentialsId: 'jenkins-gke-sa', variable: 'GKE_SA_FILE'),
    ]) {
        sh """
            apk --no-cache add bash curl python3
            curl https://sdk.cloud.google.com > install.sh
            bash install.sh --disable-prompts
            export PATH="/root/google-cloud-sdk/bin:\$PATH"

            gcloud auth activate-service-account --key-file \$GKE_SA_FILE
            gcloud auth configure-docker $registryHost

            while (! docker stats --no-stream ); do
                echo "Waiting for Docker to launch..."
                sleep 1
            done
        """
    }
}

return this