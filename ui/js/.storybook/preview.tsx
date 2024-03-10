import React from 'react';
import type { Preview } from '@storybook/react';
import { Provider } from 'react-redux';
import { setupStore } from '../src/redux/store';

const reduxDecorator = (story) => (
  <Provider store={setupStore()}>
    { story() }
  </Provider>
);

const preview: Preview = {
  decorators: [
    reduxDecorator,
  ],
  parameters: {
    actions: { argTypesRegex: '^on[A-Z].*' },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/,
      },
    },
  },
};

export default preview;
