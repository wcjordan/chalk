import {
  Image,
  ImageStyle,
  StyleSheet,
  Text,
  TextStyle,
  View,
  ViewStyle,
} from 'react-native';
import { Button } from 'react-native-paper';
import Constants from 'expo-constants';
import React, { useCallback, useEffect } from 'react';
import { maybeCompleteAuthSession } from 'expo-web-browser';
import { useAuthRequest } from 'expo-auth-session/providers/google';
import { useFonts, Roboto_500Medium } from '@expo-google-fonts/roboto';
import GoogleIcon from '../../assets/g-logo.png';

maybeCompleteAuthSession();

interface Style {
  buttonStyle: ViewStyle;
  buttonViewStyle: ViewStyle;
  iconStyle: ImageStyle;
  logoStyle: ViewStyle;
  textStyle: TextStyle;
  wrapperStyle: ViewStyle;
}

// TODO explore using PixelRatio
// https://docs.expo.dev/versions/latest/react-native/pixelratio/
const styles = StyleSheet.create<Style>({
  buttonStyle: {
    marginLeft: 0,
    marginRight: 0,
    marginTop: 0,
    marginBottom: 0,
  },
  buttonViewStyle: {
    alignItems: 'center',
    flexDirection: 'row',
    height: 40,
    justifyContent: 'center',
  },
  iconStyle: {
    width: 18,
    height: 18,
  },
  logoStyle: {
    alignItems: 'center',
    backgroundColor: 'white',
    height: 38,
    justifyContent: 'center',
    marginLeft: 1,
    width: 34,
  },
  textStyle: {
    marginLeft: 8,
    marginRight: 8,
  },
  wrapperStyle: {
    display: 'flex',
    flexDirection: 'row',
  },
});

// Used to login w/ Google OAuth for mobile workflows
const Login: React.FC<Props> = function (props: Props) {
  const { addNotification, completeAuthentication } = props;

  const [fontsLoaded] = useFonts({
    Roboto_500Medium,
  });

  const [request, response, promptAsync] = useAuthRequest({
    expoClientId: Constants.manifest?.extra?.EXPO_CLIENT_ID,
  });
  const promptLogin = useCallback(() => promptAsync(), [promptAsync]);

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

  if (!fontsLoaded) {
    return null; // TODO loading indicator
  }

  const theme = {
    colors: {
      primary: '#4285F4',
    },
    fonts: {
      medium: {
        fontFamily: 'Roboto_500Medium',
      },
    },
    roundness: 0,
  };

  return (
    <View style={styles.wrapperStyle}>
      <Button
        labelStyle={styles.buttonStyle}
        disabled={!request}
        mode="contained"
        onPress={promptLogin}
        theme={theme}
        uppercase={false}
      >
        <View style={styles.buttonViewStyle}>
          <View style={styles.logoStyle}>
            <Image
              resizeMode="center"
              source={GoogleIcon}
              style={styles.iconStyle}
            />
          </View>
          <Text style={styles.textStyle}>Sign in with Google</Text>
        </View>
      </Button>
    </View>
  );
};

type Props = {
  addNotification: (text: string) => void;
  completeAuthentication: (token: string) => void;
};

export default Login;
