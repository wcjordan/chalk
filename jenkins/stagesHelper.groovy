def shouldRunIntegrationTests(changeSet) {
    if (BRANCH_NAME == 'main') {
        return true
    }

    // Check if any of the changed files are not in the excluded directories
    def excludedDirs = ['rrweb_feature_extraction', 'session_stitching', 'test_gen', 'docs']
    def integrationTestFiles = changeSet.findAll { filepath -> !excludedDirs.any { filepath.startsWith(it + '/') } }
    return integrationTestFiles.size() > 0
}

return this