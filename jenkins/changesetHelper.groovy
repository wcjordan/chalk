def getChangeSetToTest() {
    // Fetch main so that it's available to diff against
    echo "Starting test"
    sh 'git fetch origin refs/heads/main:refs/remotes/origin/main'
    echo "Testing"
    sh 'git status'
    sh 'git branch -a'
    sh 'git diff --name-only origin/main...'
    def changeSet = sh (
        script: 'git diff --name-only origin/main...',
        returnStdout: true
    ).trim()

    if (changeSet) {
        changeSet = changeSet.split('\n').collect { it.trim() }.findAll { it }
    } else {
        changeSet = []
    }
    return changeSet
}

return this