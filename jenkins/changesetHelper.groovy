/**
 * Helper functions for working with change sets in Jenkins pipelines.
 */

/**
 * Get the list of changed files in the current branch compared to main.
 * This function fetches the latest changes from the main branch and returns
 * a list of files that have been modified, added, or deleted.
 *
 * @return List of changed files.
 */
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
        changeSet = []
    }
    return changeSet
}

return this
