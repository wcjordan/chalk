@NonCPS
def getChangeSetToTest() {
    def changeSet = sh (
        script: 'git diff --name-only origin/main...',
        returnStdout: true
    ).trim()

    if (changeSet) {
        changeSet = changeSet.split('\n').collect { it.trim() }.findAll { it }
    } else {
        changeSet = []
    }
}

return this