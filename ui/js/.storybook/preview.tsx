import type { Preview } from '@storybook/react';
import { DefaultTheme, Provider as PaperProvider } from 'react-native-paper';
import MaterialCommunityIcon from '../__mocks__/MaterialCommunityIcon';

window.IS_STORYBOOK = true;

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
