import React, { useCallback } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { Modal } from 'react-native-paper';
import LabelChip from './LabelChip';

interface Style {
  labelPickerView: ViewStyle;
  modalView: ViewStyle;
}

const styles = StyleSheet.create<Style>({
  labelPickerView: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  modalView: {
    width: '80%',
    marginHorizontal: 'auto',
  },
});

const LabelPicker: React.FC<Props> = function (props: Props) {
  const {
    labels,
    selectedLabels,
    setTodoLabelingId,
    updateTodoLabels,
    visible,
  } = props;

  const updateTodoLabelCb = useCallback(
    (label) => {
      const labelDict = Object.assign({}, selectedLabels, {
        [label]: !selectedLabels[label],
      });
      const todoLabels = Object.keys(labelDict).reduce(
        (acc: string[], label) => {
          if (labelDict[label]) {
            acc.push(label);
          }
          return acc;
        },
        [],
      );
      updateTodoLabels(todoLabels);
    },
    [updateTodoLabels, selectedLabels],
  );

  const dismissLabeling = useCallback(() => {
    setTodoLabelingId(null);
  }, [setTodoLabelingId]);

  const chips = labels.map((label) => (
    <LabelChip
      onPress={updateTodoLabelCb}
      key={label}
      label={label}
      selected={selectedLabels[label] || false}
    />
  ));
  return (
    <Modal
      onDismiss={dismissLabeling}
      style={styles.modalView}
      visible={visible}
    >
      <View style={styles.labelPickerView} testID="label-picker">
        {chips}
      </View>
    </Modal>
  );
};

type Props = {
  labels: string[];
  selectedLabels: { [label: string]: boolean };
  setTodoLabelingId: (id: number | null) => void;
  updateTodoLabels: (labels: string[]) => void;
  visible: boolean;
};

export default LabelPicker;
