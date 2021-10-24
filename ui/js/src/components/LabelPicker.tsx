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
  const { selectedLabels, setTodoLabelingId, updateTodoLabels } = props;

  const updateTodoLabelCb = useCallback(
    (label) => {
      const label_dict = Object.assign({}, selectedLabels, {
        [label]: !selectedLabels[label],
      });
      const labels = Object.keys(label_dict).reduce((acc: string[], label) => {
        if (label_dict[label]) {
          acc.push(label);
        }
        return acc;
      }, []);
      updateTodoLabels(labels);
    },
    [updateTodoLabels, selectedLabels],
  );

  const dismissLabeling = useCallback(() => {
    setTodoLabelingId(null);
  }, [setTodoLabelingId]);

  const chips = props.labels.map((label) => (
    <LabelChip
      key={label}
      label={label}
      selected={selectedLabels[label] || false}
      updateTodoLabel={updateTodoLabelCb}
    />
  ));
  return (
    <Modal
      onDismiss={dismissLabeling}
      style={styles.modalView}
      visible={props.visible}
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
  updateTodoLabels: (labels: string[]) => void;
  setTodoLabelingId: (id: number | null) => void;
  visible: boolean;
};

export default LabelPicker;
