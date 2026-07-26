import React, { useCallback } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { Modal } from 'react-native-paper';
import { setSnoozeTodoId, updateTodo } from '../redux/reducers';
import { useAppDispatch, useAppSelector } from '../hooks/hooks';
import LabelChip from './LabelChip';

interface Style {
  snoozeMenuView: ViewStyle;
  modalView: ViewStyle;
}

const styles = StyleSheet.create<Style>({
  snoozeMenuView: {
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

function getNextWeekday(dayOfWeek: number): Date {
  const now = new Date();
  const dow = now.getDay();
  const daysToAdd = (dayOfWeek - dow + 7) % 7 || 7;
  return new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate() + daysToAdd,
    7,
    0,
    0,
    0,
  );
}

const SNOOZE_OPTIONS: { [key: string]: () => string | null } = {
  Tomorrow: () => {
    const now = new Date();
    return new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate() + 1,
      7,
      0,
      0,
      0,
    ).toISOString();
  },
  'This Saturday': () => getNextWeekday(6).toISOString(),
  'Next Week': () => getNextWeekday(1).toISOString(),
  'Next Month': () => {
    const now = new Date();
    return new Date(
      now.getFullYear(),
      now.getMonth() + 1,
      1,
      7,
      0,
      0,
      0,
    ).toISOString();
  },
  'Remove snooze': () => null,
};

const SNOOZE_OPTION_LABELS = [
  'Tomorrow',
  'This Saturday',
  'Next Week',
  'Next Month',
];

const SnoozeMenu: React.FC<Props> = function (props: Props) {
  const { snoozeTodoId, visible } = props;
  const dispatch = useAppDispatch();

  const isSnoozed = useAppSelector((state) => {
    if (snoozeTodoId === null) return false;
    const todo = state.todosApi.entries.find((t) => t.id === snoozeTodoId);
    if (!todo || !todo.snoozed_until) return false;
    return new Date(todo.snoozed_until) > new Date();
  });

  const dismiss = useCallback(() => {
    dispatch(setSnoozeTodoId(null));
  }, []);

  const selectOption = useCallback(
    (optionLabel: string) => {
      if (snoozeTodoId === null) return;
      const getDate = SNOOZE_OPTIONS[optionLabel];
      if (!getDate) return;
      dispatch(updateTodo({ id: snoozeTodoId, snoozed_until: getDate() }));
      dispatch(setSnoozeTodoId(null));
    },
    [snoozeTodoId],
  );

  const chips = SNOOZE_OPTION_LABELS.map((label) => (
    <LabelChip key={label} label={label} onPress={selectOption} />
  ));

  if (isSnoozed) {
    chips.push(
      <LabelChip
        key="remove-snooze"
        label="Remove snooze"
        onPress={selectOption}
      />,
    );
  }

  return (
    <Modal
      onDismiss={dismiss}
      contentContainerStyle={styles.modalView}
      visible={visible}
    >
      <View style={styles.snoozeMenuView} testID="snooze-menu">
        {chips}
      </View>
    </Modal>
  );
};

type Props = {
  snoozeTodoId: number | null;
  visible: boolean;
};

export default SnoozeMenu;
