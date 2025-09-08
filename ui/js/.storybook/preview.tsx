import type { Preview } from '@storybook/react';
import { PaperProvider } from 'react-native-paper';
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
      >
        <Story />
      </PaperProvider>
    ),
  ],
};

export default preview;
