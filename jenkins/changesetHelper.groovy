@NonCPS
def _convertChangeSetToFilePaths(changeSets) {
    return changeSets.collectMany { changeLogSet ->
        changeLogSet.getItems().collectMany { entry ->
            entry.getAffectedFiles().collect { file ->
                file.getPath()
            }
        }
    }.unique()
}

@NonCPS
def getChangeSetToTest() {
    def changeSet = _convertChangeSetToFilePaths(currentBuild.changeSets)
    def cBuild = currentBuild.previousBuild
    while (cBuild != null) {
        // If the previous build didn't succeed, we include its changeset as needing to be tested.
        // Keep working backwards until we find a build that succeeded.
        if (cBuild.result == "SUCCESS") {
            break
        }
        changeSet = changeSet + _convertChangeSetToFilePaths(previousBuild.changeSets)
        cBuild = cBuild.previousBuild
    }
    return changeSet
}

return this