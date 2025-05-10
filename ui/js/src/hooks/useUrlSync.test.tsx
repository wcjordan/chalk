import '../__mocks__/matchMediaMock';
import { renderHook } from '@testing-library/react-hooks';
import { setFilters, toggleShowCompletedTodos } from '../redux/reducers';
import { FILTER_STATUS } from '../redux/types';
import { useUrlSync } from './useUrlSync';

// Mock the necessary dependencies
jest.mock('react-native', () => ({
  Platform: {
    OS: 'web',
  },
}));

// Initial state for the filters on the workspace
const mockWorkspaceState = {
  filterLabels: { Unlabeled: FILTER_STATUS.Active },
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
      pathname: '/todos',
      search: '',
      href: 'https://chalk.flipperkid.com/todos',
    } as unknown as Location;

    window.history.replaceState = jest.fn();
  });

  afterEach(() => {
    // Restore original location
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

    // Mock filter state
    mockWorkspaceState.filterLabels = {
      work: FILTER_STATUS.Active,
      urgent: FILTER_STATUS.Inverted,
    };
    mockWorkspaceState.showCompletedTodos = true;

    rerender();

    // Verify history.replaceState was called with the correct URL
    expect(window.history.replaceState).toHaveBeenCalledWith(
      {},
      '',
      '/todos?labels=work&inverted=urgent&showCompleted=true'
    );

    // Verify switching back to the default Inbox filters (just Unlabeled active)
    // removes the query params
    mockWorkspaceState.filterLabels = { Unlabeled: FILTER_STATUS.Active };
    mockWorkspaceState.showCompletedTodos = false;

    rerender();

    // Verify history.replaceState was called with URL without query params
    expect(window.history.replaceState).toHaveBeenCalledWith(
      {},
      '',
      '/todos'
    );
  });
});
