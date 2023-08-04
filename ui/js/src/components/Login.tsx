// import {
//   Image,
//   ImageStyle,
//   StyleSheet,
//   Text,
//   TextStyle,
//   View,
//   ViewStyle,
// } from 'react-native';
// import { Surface, TouchableRipple } from 'react-native-paper';
import React, { useCallback, useState } from 'react';
// import { maybeCompleteAuthSession } from 'expo-web-browser';
// import { useAuthRequest } from 'expo-auth-session/providers/google';
// import { useFonts, Roboto_500Medium } from '@expo-google-fonts/roboto';
import {
  GoogleSignin,
  GoogleSigninButton,
  statusCodes,
} from '@react-native-google-signin/google-signin';

// import GoogleIcon from '../../assets/g-logo.png';
import { getEnvFlags } from '../helpers';

// maybeCompleteAuthSession();
GoogleSignin.configure({
  webClientId: getEnvFlags().EXPO_CLIENT_ID,
});

// interface Style {
//   buttonStyle: ViewStyle;
//   iconStyle: ImageStyle;
//   logoStyle: ViewStyle;
//   surfaceStyle: ViewStyle;
//   textStyle: TextStyle;
//   wrapperStyle: ViewStyle;
// }

// // TODO explore using PixelRatio
// // https://docs.expo.dev/versions/latest/react-native/pixelratio/
// const styles = StyleSheet.create<Style>({
//   buttonStyle: {
//     alignItems: 'center',
//     flexDirection: 'row',
//     height: 40,
//     justifyContent: 'center',
//   },
//   iconStyle: {
//     width: 18,
//     height: 18,
//   },
//   logoStyle: {
//     alignItems: 'center',
//     backgroundColor: 'white',
//     height: 38,
//     justifyContent: 'center',
//     marginLeft: 1,
//     width: 34,
//   },
//   surfaceStyle: {
//     backgroundColor: '#4285F4',
//     borderRadius: 0,
//     borderWidth: 0,
//     minWidth: 64,
//   },
//   textStyle: {
//     color: 'white',
//     fontFamily: 'Roboto_500Medium',
//     marginLeft: 8,
//     marginRight: 8,
//   },
//   wrapperStyle: {
//     display: 'flex',
//     flexDirection: 'row',
//     paddingTop: 48,
//     justifyContent: 'center',
//   },
// });

// Used to login w/ Google OAuth for mobile workflows
const Login: React.FC<Props> = function (props: Props) {
  const { addNotification, completeAuthentication } = props;

  const [inProgress, setInProgress] = useState(false);

  //   const [fontsLoaded] = useFonts({
  //     Roboto_500Medium,
  //   });

  //   const [, response, promptAsync] = useAuthRequest(
  //     {
  //       expoClientId: getEnvFlags().EXPO_CLIENT_ID,
  //       androidClientId: getEnvFlags().ANDROID_CLIENT_ID,
  //     },
  //     {
  //       projectNameForProxy: '@flipperkid/chalk',
  //     },
  //   );
  //   const promptLogin = useCallback(
  //     () =>
  //       promptAsync({
  //         projectNameForProxy: '@flipperkid/chalk',
  //       }),
  //     [promptAsync],
  //   );

  //   useEffect(() => {
  //     if (response?.type === 'success') {
  //       const { authentication } = response;

  //       if (authentication && authentication['accessToken']) {
  //         completeAuthentication(authentication['accessToken']);
  //       } else {
  //         addNotification(
  //           'Unexpectedly missing access token.  Please refresh and login again.',
  //         );
  //         throw new Error(`Missing access token\n${authentication}`);
  //       }
  //     } else if (response) {
  //       addNotification('Login failed');
  //     }
  //   }, [response]);

  //   if (!fontsLoaded) {
  //     return null; // TODO loading indicator
  //   }

  const signIn = useCallback(async () => {
    setInProgress(true);
    try {
      await GoogleSignin.hasPlayServices();
      await GoogleSignin.signIn();
      const tokens = await GoogleSignin.getTokens();
      completeAuthentication(tokens.accessToken);
      setInProgress(false);
    } catch (error: any) {
      // eslint-disable-line @typescript-eslint/no-explicit-any
      let message = 'Login Error: unknown error';
      if (error.code === statusCodes.SIGN_IN_CANCELLED) {
        message = 'Login Error: us cancelled the login';
      } else if (error.code === statusCodes.IN_PROGRESS) {
        message = 'Login Error: a login is already in progress';
      } else if (error.code === statusCodes.PLAY_SERVICES_NOT_AVAILABLE) {
        message = 'Login Error: Play Services is not available';
      }

      console.log(message);
      addNotification(message);
      setInProgress(false);
    }
  }, [completeAuthentication, addNotification, setInProgress]);

  return (
    <GoogleSigninButton
      size={GoogleSigninButton.Size.Wide}
      color={GoogleSigninButton.Color.Light}
      onPress={signIn}
      disabled={inProgress}
    />
  );
  //     <View style={styles.wrapperStyle}>
  //       <Surface style={styles.surfaceStyle}>
  //         <TouchableRipple
  //           accessibilityRole="button"
  //           accessibilityState={{ disabled: false }}
  //           borderless
  //           disabled={false}
  //           onPress={promptLogin}
  //           rippleColor="rgba(0, 0, 0, 0.32)"
  //         >
  //           <View style={styles.buttonStyle}>
  //             <View style={styles.logoStyle}>
  //               <Image
  //                 resizeMode="center"
  //                 source={GoogleIcon}
  //                 style={styles.iconStyle}
  //               />
  //             </View>
  //             <Text style={styles.textStyle}>Sign in with Google</Text>
  //           </View>
  //         </TouchableRipple>
  //       </Surface>
  //     </View>
};

type Props = {
  addNotification: (text: string) => void;
  completeAuthentication: (token: string) => void;
};

export default Login;
