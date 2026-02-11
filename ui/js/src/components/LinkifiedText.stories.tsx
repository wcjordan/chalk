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

export const PlainText: React.FC = () =>
  wrapper(
    <LinkifiedText testID="plain-text">
      This is plain text without any links
    </LinkifiedText>,
  );

export const SingleLink: React.FC = () =>
  wrapper(
    <LinkifiedText testID="single-link">
      Check https://example.com for more info
    </LinkifiedText>,
  );

export const MultipleLinks: React.FC = () =>
  wrapper(
    <LinkifiedText testID="multiple-links">
      Visit https://example.com or http://test.com for more information
    </LinkifiedText>,
  );

export const LinkAtStart: React.FC = () =>
  wrapper(
    <LinkifiedText testID="link-at-start">
      https://example.com is a great site
    </LinkifiedText>,
  );

export const LinkAtEnd: React.FC = () =>
  wrapper(
    <LinkifiedText testID="link-at-end">
      For more info, visit https://example.com
    </LinkifiedText>,
  );

export const LinkWithPath: React.FC = () =>
  wrapper(
    <LinkifiedText testID="link-with-path">
      Read the docs at https://example.com/docs/getting-started
    </LinkifiedText>,
  );

export const LinkWithQuery: React.FC = () =>
  wrapper(
    <LinkifiedText testID="link-with-query">
      Search results: https://example.com/search?q=react+native&page=1
    </LinkifiedText>,
  );

export const MultilineWithLinks: React.FC = () =>
  wrapper(
    <LinkifiedText testID="multiline-links">
      {
        'First line with https://example.com\nSecond line with http://test.com\nThird line is plain'
      }
    </LinkifiedText>,
  );

export const OnlyLink: React.FC = () =>
  wrapper(
    <LinkifiedText testID="only-link">https://example.com</LinkifiedText>,
  );
