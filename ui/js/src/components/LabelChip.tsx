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
    marginBottom: 0,
    marginTop: 0,
  },
});

const LabelChip: React.FC<Props> = function (props: Props) {
  const { label, selected, updateTodoLabel } = props;
  const style = selected ? styles.chipSelectedStyle : styles.chipStyle;

  const selectLabel = useCallback(() => {
    updateTodoLabel(label);
  }, [label, updateTodoLabel]);

  return (
    <Chip
      style={style}
      textStyle={styles.chipTextStyle}
      onPress={selectLabel}
      selected={selected}
    >
      {props.label}
    </Chip>
  );
};

type Props = {
  label: string;
  selected: boolean;
  updateTodoLabel: (label: string) => void;
};

export default LabelChip;
