import React, { useCallback } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { WorkContext } from '../redux/types';
import LabelChip from './LabelChip';

interface Style {
  filterView: ViewStyle;
}

const styles = StyleSheet.create<Style>({
  filterView: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    width: '100%',
    backgroundColor: '#d9f0ffff',
  },
});

const WorkContextFilter: React.FC<Props> = function (props: Props) {
  const { activeWorkContext, setWorkContext, workContexts } = props;

  const setWorkContextCb = useCallback(
    (workContext: string) => {
      setWorkContext(workContext);
    },
    [setWorkContext],
  );

  const chips = Object.keys(workContexts).map((workContext) => (
    <LabelChip
      display={workContexts[workContext].displayName}
      key={workContext}
      label={workContext}
      onPress={setWorkContextCb}
      selected={workContext === activeWorkContext}
    />
  ));
  return (
    <View style={styles.filterView} testID="work-context-filter">
      {chips}
    </View>
  );
};

type Props = {
  activeWorkContext: string | undefined;
  setWorkContext: (workContext: string) => void;
  workContexts: { [key: string]: WorkContext };
};

export default WorkContextFilter;
