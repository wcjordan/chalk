import { useEffect } from 'react';
import { Platform } from 'react-native';
import { useAppDispatch, useAppSelector } from './hooks';
import { FILTER_STATUS } from '../redux/types';
import { toggleLabel, toggleShowCompletedTodos } from '../redux/reducers';

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