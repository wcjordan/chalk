import { ViewProps } from 'react-native';

interface Color {
    Dark: 'dark',
    Light: 'light',
}

interface nativeSizes {
    Icon: number,
    Standard: number,
    Wide: number,
}

declare module "@react-native-google-signin/google-signin" {
    interface GoogleSigninButtonProps extends ViewProps {
        size?: number;
        color?: 'dark' | 'light';
        disabled?: boolean;
        onPress?: () => void;
    }
    function GoogleSigninButton(props: GoogleSigninButtonProps)
    namespace GoogleSigninButton {
        export const Size: nativeSizes;
        export const Color: Color;
    }
}