import React from 'react';
import { workContexts } from '../redux/workspaceSlice';
import WorkContextFilter from './WorkContextFilter';

const defaultProps = {
  activeWorkContext: undefined,
  workContexts: workContexts,
};

export default {
  title: 'Work Context Filter',
  component: WorkContextFilter,
};
export const DefaultWorkContextFilter: React.FC = () => (
  <WorkContextFilter {...defaultProps} />
);

export const ActiveWorkContextFilter: React.FC = () => (
  <WorkContextFilter {...defaultProps} activeWorkContext="urgent" />
);
