import React from 'react';
import ErrorBar from './ErrorBar';

const defaultProps = {
  text: 'Snacks!',
};

export default {
  title: 'Error Bar',
  component: ErrorBar,
};
export const DefaultErrorBar: React.FC = () => <ErrorBar {...defaultProps} />;
