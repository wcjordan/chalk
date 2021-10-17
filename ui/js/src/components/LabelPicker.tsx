import React from 'react';
import { StyleSheet, TextStyle, View, ViewStyle } from 'react-native';
import { Chip, Modal } from 'react-native-paper';

interface Style {
  chipStyle: ViewStyle;
  chipSelectedStyle: ViewStyle;
  chipTextStyle: TextStyle;
  labelPickerView: ViewStyle;
  modalView: ViewStyle;
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
  // const { selectLabel } = props;
  // const [textValue, setTextValue] = useState('');

  // const selectLabelCb = useCallback((label) => {
  //   selectLabel(label)
  // }, [selectLabel]);

  const chips = props.labels.map((label) => (
    <LabelChip
      key={label}
      labelName={label}
      labelId={1}
      selected={props.selectedLabels[label] || false}
    />
  ));
  return (
    <Modal style={styles.modalView} visible={props.visible}>
      <View style={styles.labelPickerView}>{chips}</View>
    </Modal>
  );
};

type Props = {
  labels: string[];
  selectedLabels: { [label: string]: boolean };
  // selectLabel: (label: string) => void;
  visible: boolean;
};

const LabelChip: React.FC<ChipProps> = function (props: ChipProps) {
  const style = props.selected ? styles.chipSelectedStyle : styles.chipStyle;
  return (
    <Chip
      style={style}
      textStyle={styles.chipTextStyle}
      onPress={() => console.log(props.labelId)}
      selected={props.selected}
    >
      {props.labelName}
    </Chip>
  );
};

type ChipProps = {
  labelName: string;
  labelId: number;
  selected: boolean;
};
export default LabelPicker;
