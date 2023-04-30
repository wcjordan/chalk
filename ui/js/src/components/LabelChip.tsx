import React, { useCallback } from 'react';
import { StyleSheet, TextStyle, ViewStyle } from 'react-native';
import { Chip } from 'react-native-paper';
import { FILTER_STATUS } from '../redux/types';

interface Style {
  chipActiveStyle: ViewStyle;
  chipInvertedStyle: ViewStyle;
  chipStyle: ViewStyle;
  chipTextStyle: TextStyle;
}

const styles = StyleSheet.create<Style>({
  chipActiveStyle: {
    margin: 3,
    backgroundColor: '#a3d5ffff',
  },
  chipInvertedStyle: {
    margin: 3,
    backgroundColor: '#ffb347ff',
  },

  chipStyle: {
    margin: 3,
    backgroundColor: '#d9f0ffff',
  },
  chipTextStyle: {
    fontFamily: 'sans-serif',
    marginBottom: 0,
    marginLeft: 8,
    marginRight: 8,
    marginTop: 0,
  },
});

const LabelChip: React.FC<Props> = function (props: Props) {
  const { display, label, status, onPress } = props;
  const readOnlyDisplay = onPress === undefined;

  let style = styles.chipStyle;
  let testId = 'chip';
  if (status === FILTER_STATUS.Active || readOnlyDisplay) {
    style = styles.chipActiveStyle;
    testId = 'chip-active';
  } else if (status === FILTER_STATUS.Inverted) {
    style = styles.chipInvertedStyle;
    testId = 'chip-inverted';
  }

  const selectLabel = useCallback(() => {
    if (onPress) {
      onPress(label);
    }
  }, [label, onPress]);

  return (
    <Chip
      onPress={readOnlyDisplay ? undefined : selectLabel}
      selected={
        status === FILTER_STATUS.Active || status === FILTER_STATUS.Inverted
      }
      style={style}
      testID={testId}
      textStyle={styles.chipTextStyle}
    >
      {display || label}
    </Chip>
  );
};

type Props = {
  display?: string;
  label: string;
  onPress?: (label: string) => void;
  status?: FILTER_STATUS;
};

export default LabelChip;
