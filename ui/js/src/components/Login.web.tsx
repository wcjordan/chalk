import React from 'react';

// Used to login w/ Google OAuth for mobile workflows
const Login: React.FC<Props> = function (props: Props) {
  throw new Error('The Login component is not supported on the web');
};

type Props = {
  addNotification: (text: string) => void;
  completeAuthentication: (token: string) => void;
};

export default Login;
