// react-native-paper/refs/heads/main/src/components/MaterialCommunityIcon.tsx
// modified to remove requires in a try catch so vite can handle the impports
import * as React from 'react';
import { ComponentProps } from 'react';
import { StyleSheet, Text, Platform, Role, ViewProps } from 'react-native';

import IconModule from '@expo/vector-icons/MaterialCommunityIcons';

export type IconProps = {
  name: ComponentProps<typeof MaterialCommunityIcons>['name'];
  color?: string;
  size: number;
  direction: 'rtl' | 'ltr';
  allowFontScaling?: boolean;
  testID?: string;
};

type AccessibilityProps =
  | {
      role?: Role;
      focusable?: boolean;
    }
  | {
      accessibilityElementsHidden?: boolean;
      importantForAccessibility?: 'auto' | 'yes' | 'no' | 'no-hide-descendants';
    };

export const accessibilityProps: AccessibilityProps =
  Platform.OS === 'web'
    ? {
        role: 'img',
        focusable: false,
      }
    : {
        accessibilityElementsHidden: true,
        importantForAccessibility: 'no-hide-descendants',
      };

type IconModuleType = React.ComponentType<
  React.ComponentProps<
    | typeof import('@react-native-vector-icons/material-design-icons').default
    | typeof import('react-native-vector-icons/MaterialCommunityIcons').default
  > & {
    color: string;
    pointerEvents?: ViewProps['pointerEvents'];
  }
>;

/**
 * Fallback component displayed when no icon library is available
 */
const FallbackIcon = ({ name, color, size, ...rest }: IconProps) => {
  console.warn(
    `Tried to use the icon '${name}' in a component from 'react-native-paper', but none of the required icon libraries are installed.`,
    `To fix this, please install one of the following:\n` +
      `- @expo/vector-icons\n` +
      `- @react-native-vector-icons/material-design-icons\n` +
      `- react-native-vector-icons\n\n` +
      `You can also use another method to specify icon: https://callstack.github.io/react-native-paper/docs/guides/icons`
  );

  return (
    <Text
      {...rest}
      style={[styles.icon, { color, fontSize: size }]}
      selectable={false}
    >
      □
    </Text>
  );
};

const MaterialCommunityIcons: IconModuleType = IconModule || FallbackIcon;

/**
 * Default icon component that handles icon rendering with proper styling and accessibility
 */
const DefaultIcon = ({
  name,
  color = '#000000',
  size,
  direction,
  allowFontScaling,
  testID,
}: IconProps) => {
  return (
    <MaterialCommunityIcons
      allowFontScaling={allowFontScaling}
      name={name}
      color={color}
      size={size}
      style={[
        {
          transform: [{ scaleX: direction === 'rtl' ? -1 : 1 }],
          lineHeight: size,
        },
        styles.icon,
      ]}
      pointerEvents="none"
      selectable={false}
      testID={testID}
      {...accessibilityProps}
    />
  );
};

const styles = StyleSheet.create({
  icon: {
    backgroundColor: 'transparent',
  },
});

export default DefaultIcon;