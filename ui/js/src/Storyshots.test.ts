import './__mocks__/matchMediaMock';

import initStoryshots from '@storybook/addon-storyshots';

beforeAll(function () {
  // Stub Math.random so aria-labelledby is deterministic for font-awesome
  jest.spyOn(global.Math, 'random').mockImplementation(() => 0.5);

  jest.mock('react-native/Libraries/Animated/NativeAnimatedHelper');
});

initStoryshots();
