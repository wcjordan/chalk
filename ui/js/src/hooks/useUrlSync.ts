import _ from 'lodash';
import { useEffect } from 'react';
import { Platform } from 'react-native';
import { FILTER_STATUS } from '../redux/types';
import { setFilters, toggleShowCompletedTodos } from '../redux/reducers';
import { useAppDispatch, useAppSelector } from './hooks';

export function useUrlSync() {
  // Only run on web platform
  if (Platform.OS !== 'web') {
    return;
  }

  const dispatch = useAppDispatch();
  const filterLabels = useAppSelector((state) => state.workspace.filterLabels);
  const showCompletedTodos = useAppSelector(
    (state) => state.workspace.showCompletedTodos,
  );

  // Read from URL on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const hasFilters =
      params.has('labels') ||
      params.has('inverted') ||
      params.has('showCompleted');

    if (hasFilters) {
      // Get active and inverted labels from URL
      const activeLabels =
        params.get('labels')?.split(',').filter(Boolean) || [];
      const invertedLabels =
        params.get('inverted')?.split(',').filter(Boolean) || [];

      // Apply filters in a single batch operation
      dispatch(setFilters({ activeLabels, invertedLabels }));

      // Apply completed todos visibility
      const showCompleted = params.get('showCompleted') === 'true';
      if (showCompleted !== showCompletedTodos) {
        dispatch(toggleShowCompletedTodos());
      }
    }
  }, []);

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();

    const activeLabels = Object.keys(filterLabels)
      .filter((label) => filterLabels[label] === FILTER_STATUS.Active)
      .sort();

    const invertedLabels = Object.keys(filterLabels)
      .filter((label) => filterLabels[label] === FILTER_STATUS.Inverted)
      .sort();

    // If Inbox filters, then drop query params from URL
    // Note this assumes that the Inbox is the default state and should be updated if that ever changes
    if (
      _.isEqual(activeLabels, ['Unlabeled']) &&
      invertedLabels.length === 0 &&
      !showCompletedTodos
    ) {
      window.history.replaceState({}, '', window.location.pathname);
      return;
    }

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
