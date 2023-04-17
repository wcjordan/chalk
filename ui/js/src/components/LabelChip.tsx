import React, { useCallback } from 'react';
import { StyleSheet, TextStyle, ViewStyle } from 'react-native';
import { Chip } from 'react-native-paper';

interface Style {
  chipStyle: ViewStyle;
  chipSelectedStyle: ViewStyle;
  chipTextStyle: TextStyle;
}

const styles = StyleSheet.create<Style>({
  chipStyle: {
    margin: 3,
    backgroundColor: '#d9f0ffff',
  },
  chipSelectedStyle: {
    margin: 3,
    backgroundColor: '#a3d5ffff',
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
  const { display, label, selected, onPress } = props;
  const readOnlyDisplay = onPress === undefined;
  const style =
    selected || readOnlyDisplay ? styles.chipSelectedStyle : styles.chipStyle;

  const selectLabel = useCallback(() => {
    if (onPress) {
      onPress(label);
    }
  }, [label, onPress]);

  return (
    <Chip
      onPress={readOnlyDisplay ? undefined : selectLabel}
      selected={selected}
      style={style}
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
  selected: boolean;
};

export default LabelChip;
