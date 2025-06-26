/**
 * This script is used in Jenkins pipelines to determine whether integration tests should be run
 */

/**
 * Check if integration tests should be run based on the changed files in the current branch.
 * Run the integration tests if the branch is 'main' or if there are any changes in files that
 * are not in the excluded directories.
 */
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
