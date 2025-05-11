// The jest-serializer-html package is available as a dependency of the test-runner
const jestSerializerHtml = require('jest-serializer-html');

const LOADING_INDICATOR_PATTERN = /rotate\(-?\d+\.?\d*deg\)/g;

module.exports = {
  /*
   * The test-runner calls the serialize function when the test reaches the expect(SomeHTMLElement).toMatchSnapshot().
   * It will replace all dynamic values with a mocked value so that the snapshot is consistent.
   * For instance, the loading indicator rotate css style will be replaced with 'rotate(mocked_deg)'.
   */
  serialize(val) {
    const cleanedHtml = val.replace(
      LOADING_INDICATOR_PATTERN,
      'rotate(mocked_deg)',
    );
    return jestSerializerHtml.print(cleanedHtml);
  },
  test(val) {
    return jestSerializerHtml.test(val);
  },
};
