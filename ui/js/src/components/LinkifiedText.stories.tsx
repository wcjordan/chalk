import React from 'react';
import { StyleSheet, View } from 'react-native';
import LinkifiedText from './LinkifiedText';

const styles = StyleSheet.create({
  wrapper: {
    padding: 16,
  },
});

const wrapper = (component) => <View style={styles.wrapper}>{component}</View>;

export default {
  title: 'LinkifiedText',
  component: LinkifiedText,
};

export const SingleLink: React.FC = () =>
  wrapper(
    <LinkifiedText testID="single-link">
      Read the docs at https://example.com/docs/getting-started
    </LinkifiedText>,
  );

export const OnlyLink: React.FC = () =>
  wrapper(
    <LinkifiedText testID="only-link">https://example.com</LinkifiedText>,
  );

export const PlainText: React.FC = () =>
  wrapper(
    <LinkifiedText testID="plain-text">
      This is plain text without any links
    </LinkifiedText>,
  );

export const MultipleLinks: React.FC = () =>
  wrapper(
    <LinkifiedText testID="multiple-links">
      {
        'Visit https://example.com or see search results:\nhttps://example.com/search?q=react+native&page=1 for more info'
      }
    </LinkifiedText>,
  );

export const LinkAtEnd: React.FC = () =>
  wrapper(
    <LinkifiedText testID="link-at-end">
      For more info, visit https://example.com!
    </LinkifiedText>,
  );
