Approach

Since you're using React Native for web, you'll need a solution that works well with your existing Redux setup. While redux-router (or more specifically, connected-react-router or the newer
redux-first-history) could be useful, for your specific case of just wanting to sync filter states with the URL, you might not need the full router integration.

Here's how you could implement this:

1. Use URL Query Parameters

You can use URL query parameters to represent your filter state. For example:

 • ?labels=work,home&inverted=urgent&showCompleted=true

2. Implementation Steps

Step 1: Add URL Sync Logic

Create a new file src/hooks/useUrlSync.ts:


import { useEffect } from 'react';
import { Platform } from 'react-native';
import { useAppDispatch, useAppSelector } from './hooks';
import { FILTER_STATUS } from '../redux/types';
import { setWorkContext, toggleLabel, toggleShowCompletedTodos } from '../redux/reducers';

export function useUrlSync() {
  const dispatch = useAppDispatch();
  const filterLabels = useAppSelector(state => state.workspace.filterLabels);
  const showCompletedTodos = useAppSelector(state => state.workspace.showCompletedTodos);

  // Only run on web platform
  if (Platform.OS !== 'web') {
    return;
  }

  // Read from URL on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);

    // Clear existing filters first
    const currentFilters = Object.keys(filterLabels);
    currentFilters.forEach(label => {
      if (filterLabels[label] !== undefined) {
        dispatch(toggleLabel(label));
      }
    });

    // Apply active filters from URL
    const activeLabels = params.get('labels')?.split(',') || [];
    activeLabels.forEach(label => {
      if (label) dispatch(toggleLabel(label));
    });

    // Apply inverted filters from URL
    const invertedLabels = params.get('inverted')?.split(',') || [];
    invertedLabels.forEach(label => {
      if (label) {
        dispatch(toggleLabel(label)); // First make it active
        dispatch(toggleLabel(label)); // Then make it inverted
      }
    });

    // Apply work context if specified
    const workContext = params.get('context');
    if (workContext) {
      dispatch(setWorkContext(workContext));
    }

    // Apply completed todos visibility
    const showCompleted = params.get('showCompleted') === 'true';
    if (showCompleted !== showCompletedTodos) {
      dispatch(toggleShowCompletedTodos());
    }
  }, []);

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();

    const activeLabels = Object.keys(filterLabels).filter(
      label => filterLabels[label] === FILTER_STATUS.Active
    );

    const invertedLabels = Object.keys(filterLabels).filter(
      label => filterLabels[label] === FILTER_STATUS.Inverted
    );

    if (activeLabels.length > 0) {
      params.set('labels', activeLabels.join(','));
    }

    if (invertedLabels.length > 0) {
      params.set('inverted', invertedLabels.join(','));
    }

    if (showCompletedTodos) {
      params.set('showCompleted', 'true');
    }

    // Update URL without reloading the page
    const newUrl = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
    window.history.replaceState({}, '', newUrl);
  }, [filterLabels, showCompletedTodos]);
}


Step 2: Use the Hook in TodoList Component

Modify src/components/TodoList.tsx to use the new hook:


import { useUrlSync } from '../hooks/useUrlSync';

const TodoList: React.FC = memo(function () {
  const dispatch = useAppDispatch()
  useDataLoader();
  useUrlSync(); // Add this line
  if (Platform.OS === 'web') {
    useSessionRecorder();
  }

  // Rest of the component remains the same
  // ...
});


Step 3: Create a Hook Index File

Create or update src/hooks/index.ts to export all hooks:


export * from './hooks';
export * from './useSessionRecorder';
export * from './useUrlSync';


Considerations

 1 Mobile Compatibility: The implementation above only runs on web, so it won't affect your mobile app.
 2 Deep Linking: If you want similar functionality on mobile, you'd need to implement deep linking, which is a separate topic.
 3 Performance: The implementation uses useEffect to avoid infinite loops, but be careful about the dependency arrays.
 4 Work Contexts: The implementation above handles work contexts, but you might need to adjust it based on how you want to represent them in the URL.

This approach gives you URL-based filtering without needing to add a full router library, which might be overkill for just syncing filter state with the URL.