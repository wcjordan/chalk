import React from 'react';
import { Linking, Platform, StyleSheet, TextStyle } from 'react-native';
import { Text } from 'react-native-paper';
import { parseTextWithUrls } from '../utils/urlParser';

interface LinkifiedTextProps {
  children: string;
  style?: TextStyle;
  testID?: string;
}

const styles = StyleSheet.create({
  link: {
    color: '#1976d2',
    textDecorationLine: 'underline',
  },
});

/**
 * Component that renders text with clickable URLs
 * URLs are automatically detected and styled as links
 */
const LinkifiedText: React.FC<LinkifiedTextProps> = ({
  children,
  style,
  testID,
}) => {
  const segments = parseTextWithUrls(children);

  const handleLinkPress = (url: string) => {
    if (Platform.OS === 'web') {
      // On web, open in a new tab
      window.open(url, '_blank', 'noopener,noreferrer');
    } else {
      // On native, use Linking API
      Linking.openURL(url).catch((err) => {
        console.error('Failed to open URL:', url, err);
      });
    }
  };

  // If no URLs found, render plain text
  if (segments.length === 0 || segments.every((seg) => seg.type === 'text')) {
    return (
      <Text style={style} testID={testID}>
        {children}
      </Text>
    );
  }

  return (
    <Text style={style} testID={testID}>
      {segments.map((segment, index) => {
        if (segment.type === 'url') {
          return (
            <Text
              key={index}
              style={styles.link}
              onPress={() => handleLinkPress(segment.content)}
              testID={`${testID}-link-${index}`}
              accessibilityRole="link"
            >
              {segment.content}
            </Text>
          );
        }
        return (
          <Text key={index} testID={`${testID}-text-${index}`}>
            {segment.content}
          </Text>
        );
      })}
    </Text>
  );
};

export default LinkifiedText;
