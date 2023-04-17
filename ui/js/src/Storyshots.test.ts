import './__mocks__/matchMediaMock';
import initStoryshots from '@storybook/addon-storyshots';
import mockSafeAreaContext from 'react-native-safe-area-context/jest/mock';

global.setImmediate = () => null;
global.clearImmediate = () => null;
jest.mock('expo-font');
jest.mock('react-native/Libraries/Animated/NativeAnimatedHelper');
jest.mock('react-native-safe-area-context', () => mockSafeAreaContext);

beforeAll(function () {
  // Stub Math.random so aria-labelledby is deterministic for font-awesome
  jest.spyOn(global.Math, 'random').mockImplementation(() => 0.5);
});

initStoryshots();
