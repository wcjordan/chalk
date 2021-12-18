import { Button, Platform } from 'react-native';
import Constants from 'expo-constants';
import React, { useEffect } from 'react';
import { maybeCompleteAuthSession } from 'expo-web-browser';
import { useAuthRequest } from 'expo-auth-session/providers/google';

maybeCompleteAuthSession();

const Login: React.FC<Props> = function (props: Props) {
  // const { completeAuthentication, loadSessionCookie } = props;
  const { completeAuthentication } = props;
  const isWeb = Platform.select({
    native: false,
    default: true,
  });
  if (isWeb) {
    return null;
  }

  const [request, response, promptAsync] = useAuthRequest({
    expoClientId: Constants.manifest?.extra?.EXPO_CLIENT_ID,
  });

  // useEffect(loadSessionCookie, []);
  useEffect(() => {
    if (response?.type === 'success') {
      const { authentication } = response;

      if (authentication && authentication['accessToken']) {
        completeAuthentication(authentication['accessToken']);
      }
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
  completeAuthentication: (token: string) => void;
  loadSessionCookie: () => void;
};

export default Login;
