import React, { useCallback, useState } from 'react';
import { Snackbar } from 'react-native-paper';
import { dismissNotification } from '../redux/reducers';
import { useAppDispatch } from '../hooks';

const ErrorBar: React.FC<Props> = function (props: Props) {
  const { permanent, text } = props;
  const [visible, setVisible] = useState(text != null);

  const dispatch = useAppDispatch();
  const dismissCb = useCallback(() => {
    if (text == null || permanent) {
      return;
    }

    setVisible(false);
    dispatch(dismissNotification());
  }, [text]);

  return (
    <Snackbar
      onDismiss={dismissCb}
      theme={{
        colors: {
          surface: '#444',
          onSurface: '#FAA0A0',
        },
      }}
      visible={visible}
    >
      {text}
    </Snackbar>
  );
};

type Props = {
  permanent?: boolean;
  text: string | null;
};

export default ErrorBar;
