import { StyleSheet, View, ViewStyle } from 'react-native';
import React, { useCallback, useEffect, useState } from 'react';
import {
  GoogleSignin,
  GoogleSigninButton,
  statusCodes,
} from '@react-native-google-signin/google-signin';

import { getEnvFlags } from '../helpers';

GoogleSignin.configure({
  webClientId: getEnvFlags().OAUTH_CLIENT_ID,
  offlineAccess: true,
});

interface Style {
  wrapperStyle: ViewStyle;
}

const styles = StyleSheet.create<Style>({
  wrapperStyle: {
    display: 'flex',
    flexDirection: 'row',
    paddingTop: 48,
    justifyContent: 'center',
  },
});

// Used to login w/ Google OAuth for mobile workflows
const Login: React.FC<Props> = function (props: Props) {
  const { addNotification, completeAuthentication } = props;
  const [inProgress, setInProgress] = useState(false);

  const signIn = useCallback(async () => {
    setInProgress(true);
    try {
      await GoogleSignin.hasPlayServices();
      const userInfo = await GoogleSignin.signIn();

      setInProgress(false);
      if (userInfo.idToken) {
        completeAuthentication(userInfo.idToken);
      } else {
        const message =
          'Login Error: ID token unexpectedly not found after login';
        console.error(message);
        addNotification(message);
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      let message = 'Login Error: unknown error';
      if (error.code === statusCodes.SIGN_IN_CANCELLED) {
        message = 'Login Error: us cancelled the login';
      } else if (error.code === statusCodes.IN_PROGRESS) {
        message = 'Login Error: a login is already in progress';
      } else if (error.code === statusCodes.PLAY_SERVICES_NOT_AVAILABLE) {
        message = 'Login Error: Play Services is not available';
      }

      console.error(message);
      console.error(error);
      addNotification(message);
      setInProgress(false);
    }
  }, [completeAuthentication, addNotification, setInProgress]);

  useEffect(() => {
    async function autoSignIn() {
      if (await GoogleSignin.isSignedIn()) {
        signIn();
      }
    }
    autoSignIn();
  }, [signIn]);

  return (
    <View style={styles.wrapperStyle}>
      <GoogleSigninButton
        size={GoogleSigninButton.Size.Wide}
        color={GoogleSigninButton.Color.Light}
        onPress={signIn}
        disabled={inProgress}
      />
    </View>
  );
};

type Props = {
  addNotification: (text: string) => void;
  completeAuthentication: (token: string) => void;
};

export default Login;
