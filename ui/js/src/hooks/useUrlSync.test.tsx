import { renderHook } from '@testing-library/react-hooks';
import { setFilters, toggleShowCompletedTodos } from '../redux/reducers';
import { FILTER_STATUS } from '../redux/types';
import { useUrlSync } from './useUrlSync';

jest.mock('react-native', () => ({
  Platform: {
    OS: 'web',
  },
}));

// Stubbed state object for the filters on the workspace
const mockWorkspaceState = {
  filterLabels: {},
  showCompletedTodos: false,
}
jest.mock('./hooks', () => ({
  useAppDispatch: jest.fn().mockReturnValue(jest.fn()),
  useAppSelector: jest.fn().mockImplementation((selector) => {
    return selector({ workspace: mockWorkspaceState })
  }),
}));

jest.mock('../redux/reducers', () => ({
  setFilters: jest.fn(),
  toggleShowCompletedTodos: jest.fn(),
}));

describe('useUrlSync', () => {
  let originalLocation: Location;

  beforeEach(() => {
    // Save original location
    originalLocation = window.location;

    // Mock window.location and history
    delete window.location;
    window.location = {
      ...originalLocation,
      pathname: '/',
      search: '',
    };
    window.history.replaceState = jest.fn();

    // Set mockWorkspaceState to default state
    resetMockWorkspaceState();
  });

  afterEach(() => {
    // Restore original location & clear mocks
    window.location = originalLocation;
    jest.clearAllMocks();
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

    // Verify no actions were dispatched (default state is already Unlabeled)
    expect(setFilters).not.toHaveBeenCalled();
    expect(toggleShowCompletedTodos).not.toHaveBeenCalled();
  });

  it('should update URL when filters change', () => {
    // Initial render with default filters
    const { rerender } = renderHook(() => useUrlSync());

    // Change filter state & rerender
    mockWorkspaceState.filterLabels = {
      work: FILTER_STATUS.Active,
      "5 minutes": FILTER_STATUS.Active,
      urgent: FILTER_STATUS.Inverted,
    };
    mockWorkspaceState.showCompletedTodos = true;

    rerender();

    // Verify history.replaceState was called with the correct URL
    expect(window.history.replaceState).toHaveBeenCalledWith(
      {},
      '',
      '/?labels=5+minutes%2Cwork&inverted=urgent&showCompleted=true'
    );

    // Verify switching back to the default Inbox filters removes the query params
    resetMockWorkspaceState();
    rerender();

    // Verify history.replaceState was called with URL without query params
    expect(window.history.replaceState).toHaveBeenCalledWith(
      {},
      '',
      '/'
    );
  });
});

// Reset the mock workspace state to default values
const resetMockWorkspaceState = () => {
  mockWorkspaceState.filterLabels = {};
  mockWorkspaceState.showCompletedTodos = false;
}
