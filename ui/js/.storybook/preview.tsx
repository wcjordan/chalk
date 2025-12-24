import type { Preview } from '@storybook/react';
import { DefaultTheme, Provider as PaperProvider } from 'react-native-paper';

import { sb } from 'storybook/test';
if (process.env.STORYBOOK_TEST_ENV === 'true') {
  sb.mock(import('expo-font'));
}
import MaterialCommunityIcon from '../__mocks__/MaterialCommunityIcon';

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
  tags: ['autodocs'],
  decorators: [
    (Story, _) => (
      <PaperProvider
        settings={{
          icon: (props) => <MaterialCommunityIcon {...props} />,
        }}
        theme={DefaultTheme}
      >
        <Story />
      </PaperProvider>
    ),
  ],
};

export default preview;
