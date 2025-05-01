import { StyleSheet, View, ViewStyle } from 'react-native';
import React, { useCallback, useEffect, useState } from 'react';
import {
  GoogleSignin,
  GoogleSigninButton,
  statusCodes,
} from '@react-native-google-signin/google-signin';
import {
  addNotification,
  completeAuthentication,
} from '../redux/reducers';
import { getEnvFlags } from '../helpers';
import { useAppDispatch } from '../hooks/hooks';

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
const Login: React.FC = function () {
  const dispatch = useAppDispatch();
  const [inProgress, setInProgress] = useState(false);

  const signIn = useCallback(async () => {
    setInProgress(true);
    try {
      await GoogleSignin.hasPlayServices();
      const signinData = await GoogleSignin.signIn();
      const userInfo = signinData.data;

      setInProgress(false);
      if (userInfo.idToken) {
        dispatch(completeAuthentication(userInfo.idToken));
      } else {
        const message =
          'Login Error: ID token unexpectedly not found after login';
        console.error(message);
        dispatch(addNotification(message));
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
      dispatch(addNotification(message));
      setInProgress(false);
    }
  }, [setInProgress]);

  useEffect(() => {
    async function autoSignIn() {
      if (await GoogleSignin.hasPreviousSignIn()) {
        signIn();
      }
    }
    if (getEnvFlags().ENVIRONMENT === 'test') {
      return;
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

export default Login;
