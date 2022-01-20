import { Button } from 'react-native';
import Constants from 'expo-constants';
import React, { useEffect } from 'react';
import { maybeCompleteAuthSession } from 'expo-web-browser';
import { useAuthRequest } from 'expo-auth-session/providers/google';

maybeCompleteAuthSession();

// Used to login w/ Google OAuth for mobile workflows
const Login: React.FC<Props> = function (props: Props) {
  const { addNotification, completeAuthentication } = props;
  const [request, response, promptAsync] = useAuthRequest({
    expoClientId: Constants.manifest?.extra?.EXPO_CLIENT_ID,
  });

  useEffect(() => {
    if (response?.type === 'success') {
      const { authentication } = response;

      if (authentication && authentication['accessToken']) {
        completeAuthentication(authentication['accessToken']);
      } else {
        addNotification(
          'Unexpectedly missing access token.  Please refresh and login again.',
        );
        throw new Error(`Missing access token\n${authentication}`);
      }
    } else if (response) {
      addNotification('Login failed');
    }
  }, [response]);

  return (
    <Button
      disabled={!request}
      title="Login"
      onPress={() => {
        promptAsync();
      }}
    />
  );
};

type Props = {
  addNotification: (text: string) => void;
  completeAuthentication: (token: string) => void;
};

export default Login;
