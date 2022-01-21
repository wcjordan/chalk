import React, { useCallback, useState } from 'react';
import { Snackbar } from 'react-native-paper';

const ErrorBar: React.FC<Props> = function (props: Props) {
  const { dismissNotification, permanent, text } = props;
  const [visible, setVisible] = useState(text != null);
  const dismissCb = useCallback(() => {
    if (text == null || permanent) {
      return;
    }

    setVisible(false);
    dismissNotification();
  }, [dismissNotification, text]);

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
  dismissNotification: () => void;
  permanent?: boolean;
  text: string | null;
};

export default ErrorBar;
