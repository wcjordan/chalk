describe('persistStorage', () => {
  beforeEach(() => {
    jest.resetModules();
  });

  afterEach(() => {
    jest.dontMock('react-native');
    jest.dontMock('redux-persist/lib/storage');
    jest.dontMock('@react-native-async-storage/async-storage');
  });

  it('uses redux-persist web storage on web without evaluating native storage', () => {
    const webDefault = {
      getItem: jest.fn(),
      setItem: jest.fn(),
      removeItem: jest.fn(),
    };
    const nativeModuleEvaluated = jest.fn();
    jest.doMock('react-native', () => ({ Platform: { OS: 'web' } }));
    jest.doMock('redux-persist/lib/storage', () => ({ default: webDefault }));
    jest.doMock('@react-native-async-storage/async-storage', () => {
      nativeModuleEvaluated();
      return { default: {} };
    });

    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const storage = require('./persistStorage').default;

    expect(storage).toBe(webDefault);
    expect(nativeModuleEvaluated).not.toHaveBeenCalled();
  });

  it('uses native async-storage on native without evaluating redux-persist web storage', () => {
    const nativeDefault = {
      getItem: jest.fn(),
      setItem: jest.fn(),
      removeItem: jest.fn(),
    };
    const webModuleEvaluated = jest.fn();
    jest.doMock('react-native', () => ({ Platform: { OS: 'ios' } }));
    jest.doMock('redux-persist/lib/storage', () => {
      webModuleEvaluated();
      return { default: {} };
    });
    jest.doMock('@react-native-async-storage/async-storage', () => ({
      default: nativeDefault,
    }));

    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const storage = require('./persistStorage').default;

    expect(storage).toBe(nativeDefault);
    expect(webModuleEvaluated).not.toHaveBeenCalled();
  });
});

export {};
