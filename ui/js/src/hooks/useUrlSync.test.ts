import '../__mocks__/matchMediaMock';
import { renderHook } from '@testing-library/react-hooks';
import { useUrlSync } from './useUrlSync';
import { setFilters, toggleShowCompletedTodos } from '../redux/reducers';

// Define mock constants to avoid referencing out-of-scope variables
const MOCK_FILTER_STATUS = {
  Active: 'ACTIVE',
  Inverted: 'INVERTED'
};

// Mock the necessary dependencies
jest.mock('react-native', () => ({
  Platform: {
    OS: 'web',
  },
}));

jest.mock('./hooks', () => ({
  useAppDispatch: jest.fn().mockReturnValue(jest.fn()),
  useAppSelector: jest.fn().mockImplementation((selector) => {
    if (selector.name === 'filterLabels') return { Unlabeled: MOCK_FILTER_STATUS.Active };
    if (selector.name === 'showCompletedTodos') return false;
    return selector();
  }),
}));

jest.mock('../redux/reducers', () => ({
  setFilters: jest.fn(),
  toggleShowCompletedTodos: jest.fn(),
}));

// Mock the types module
jest.mock('../redux/types', () => ({
  FILTER_STATUS: {
    Active: 'ACTIVE',
    Inverted: 'INVERTED'
  }
}));

describe('useUrlSync', () => {
  let originalLocation: Location;
  let mockDispatch: jest.Mock;
  
  beforeEach(() => {
    // Save original location
    originalLocation = window.location;
    
    // Mock window.location and history
    delete window.location;
    window.location = {
      ...originalLocation,
      pathname: '/todos',
      search: '',
      href: 'https://chalk.flipperkid.com/todos',
    } as unknown as Location;
    
    window.history.replaceState = jest.fn();
    
    // Reset mocks
    mockDispatch = require('./hooks').useAppDispatch();
    mockDispatch.mockClear();
    setFilters.mockClear();
    toggleShowCompletedTodos.mockClear();
  });
  
  afterEach(() => {
    // Restore original location
    window.location = originalLocation;
    jest.resetAllMocks();
  });
  
  it('should read filters from URL on mount', () => {
    // Set up URL with filters
    window.location.search = '?labels=work,home&inverted=urgent&showCompleted=true';
    
    renderHook(() => useUrlSync());
    
    // Verify setFilters was called with correct parameters
    expect(setFilters).toHaveBeenCalledWith({
      activeLabels: ['work', 'home'],
      invertedLabels: ['urgent'],
    });
    
    // Verify toggleShowCompletedTodos was called
    expect(toggleShowCompletedTodos).toHaveBeenCalled();
  });
  
  it('should default to Unlabeled filter when no filters in URL', () => {
    // Empty URL search
    window.location.search = '';
    
    renderHook(() => useUrlSync());
    
    // Verify setFilters was called with Unlabeled filter
    expect(setFilters).toHaveBeenCalledWith({
      activeLabels: ['Unlabeled'],
      invertedLabels: [],
    });
  });
  
  it('should update URL when filters change', () => {
    // Mock filter state
    const { useAppSelector } = require('./hooks');
    useAppSelector.mockImplementation((selector) => {
      if (selector === selectFilterLabels) {
        return {
          work: MOCK_FILTER_STATUS.Active,
          urgent: MOCK_FILTER_STATUS.Inverted,
        };
      }
      if (selector === selectShowCompletedTodos) {
        return true;
      }
      return selector();
    });
    
    renderHook(() => useUrlSync());
    
    // Verify history.replaceState was called with the correct URL
    expect(window.history.replaceState).toHaveBeenCalledWith(
      {},
      '',
      '/todos?labels=work&inverted=urgent&showCompleted=true'
    );
  });
  
  it('should remove query params when default Inbox filters are set', () => {
    // Mock filter state to be the default Inbox (just Unlabeled active)
    const { useAppSelector } = require('./hooks');
    useAppSelector.mockImplementation((selector) => {
      if (selector === selectFilterLabels) {
        return { Unlabeled: MOCK_FILTER_STATUS.Active };
      }
      if (selector === selectShowCompletedTodos) {
        return false;
      }
      return selector();
    });
    
    renderHook(() => useUrlSync());
    
    // Verify history.replaceState was called with URL without query params
    expect(window.history.replaceState).toHaveBeenCalledWith(
      {},
      '',
      '/todos'
    );
  });
});

// Helper functions to match the selectors in the hook
function selectFilterLabels(state: any) {
  return state.workspace.filterLabels;
}

function selectShowCompletedTodos(state: any) {
  return state.workspace.showCompletedTodos;
}
