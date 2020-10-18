import initStoryshots from '@storybook/addon-storyshots';

beforeAll(function () {
  // Stub Math.random so aria-labelledby is deterministic for font-awesome
  jest.spyOn(global.Math, 'random').mockImplementation(() => 0.5);
});

initStoryshots();
