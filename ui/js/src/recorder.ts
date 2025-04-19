import { record } from 'rrweb';
import Cookies from 'js-cookie';
import { Platform } from 'react-native';

import { logSessionData } from './redux/fetchApi';
import { getEnvFlags } from './helpers';


let events: any[] = [];
let sessionGuid: string = crypto.randomUUID();
const environment = getEnvFlags().ENVIRONMENT;

export function initRecorder() {
  // Don't record on mobile
  if (Platform.OS !== 'web') {
    return;
  }

  setTimeout(() => {
    record({
        emit(event) {
        // push event into the events array
        events.push(event);
        },
    });
  // Wait a second to start recording to skip page initialization
  }, 1000);
}

// this function will send events to the backend and reset the events array
function save() {
    
  const data = JSON.stringify({ 
    session_guid: sessionGuid,
    session_data: events,
    environment: environment,
  });
  const csrfToken = Cookies.get('csrftoken') as string;
  const result = logSessionData(data, csrfToken);
  result.then((response: string) => {
    console.error('Failed to save events');
    console.error(response);
  }).catch((error: string) => {
    console.error('Failed to save events');
    console.error(error);
  });
  events = [];
}

// save events every 10 seconds
setInterval(save, 10 * 1000);  
  