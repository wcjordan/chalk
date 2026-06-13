import React, { useCallback, useState } from 'react';
import { Snackbar } from 'react-native-paper';
import { dismissNotification } from '../redux/reducers';
import { useAppDispatch } from '../hooks/hooks';
import { NotificationType } from '../redux/types';

const THEME_DEFAULT = { colors: { surface: '#444', onSurface: '#FAA0A0' } };
const THEME_LABEL = { colors: { surface: '#FFFDE7', onSurface: '#5D4037' } };

const ErrorBar: React.FC<Props> = function (props: Props) {
  const { notificationType, permanent, text } = props;
  const [visible, setVisible] = useState(text != null);

  const dispatch = useAppDispatch();
  const dismissCb = useCallback(() => {
    if (text == null || permanent) {
      return;
    }

    setVisible(false);
    dispatch(dismissNotification());
  }, [text]);

  const theme = notificationType === 'label' ? THEME_LABEL : THEME_DEFAULT;

  return (
    <Snackbar
      onDismiss={dismissCb}
      theme={theme}
      testID="message-bar"
      visible={visible}
    >
      {text}
    </Snackbar>
  );
};

type Props = {
  notificationType?: NotificationType;
  permanent?: boolean;
  text: string | null;
};

export default ErrorBar;
