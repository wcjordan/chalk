import React, { useCallback } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { Modal } from 'react-native-paper';
import { FILTER_STATUS } from '../redux/types';
import { setLabelTodoId, updateTodoLabels } from '../redux/reducers';
import { useAppDispatch } from '../hooks';
import LabelChip from './LabelChip';

interface Style {
  labelPickerView: ViewStyle;
  modalView: ViewStyle;
}

const styles = StyleSheet.create<Style>({
  labelPickerView: {
    backgroundColor: 'rgba(0, 0, 0, 0.15)',
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  modalView: {
    marginLeft: 'auto',
    marginRight: 'auto',
    width: '80%',
  },
});

const LabelPicker: React.FC<Props> = function (props: Props) {
  const { labels, selectedLabels, visible } = props;
  const dispatch = useAppDispatch();

  const updateTodoLabelCb = useCallback(
    (label: string) => {
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
      dispatch(updateTodoLabels(todoLabels));
    },
    [selectedLabels],
  );

  const dismissLabeling = useCallback(() => {
    dispatch(setLabelTodoId(null));
  }, []);

  const chips = labels.map((label) => (
    <LabelChip
      onPress={updateTodoLabelCb}
      key={label}
      label={label}
      status={selectedLabels[label] ? FILTER_STATUS.Active : undefined}
    />
  ));
  return (
    <Modal
      onDismiss={dismissLabeling}
      contentContainerStyle={styles.modalView}
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
  visible: boolean;
};

export default LabelPicker;
