def getChangeSetToTest() {
    // Fetch main so that it's available to diff against
    sh 'git fetch origin refs/heads/main:refs/remotes/origin/main'
    def changeSet = sh (
        script: 'git diff --name-only origin/main...',
        returnStdout: true
    ).trim()

    if (changeSet) {
        changeSet = changeSet.split('\n').collect { it.trim() }.findAll { it }
    } else {
        changeSet = ['rrweb_feature_extraction/.pylintrc']
    }
    return []
}

return this