import type { TestRunnerConfig } from '@storybook/test-runner';

const config: TestRunnerConfig = {
  async postVisit(page, context) {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    const elementLocator = await page.locator('#storybook-root');
    const innerHTML = await elementLocator.innerHTML();
    expect(innerHTML).toMatchSnapshot();
  },
};

export default config;
