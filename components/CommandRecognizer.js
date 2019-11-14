import React from 'react';
import { AsyncStorage, StyleSheet } from 'react-native';
import { Text, ActivityIndicator } from 'react-native-paper';

export default function CommandRecognizer(props) {
    React.useEffect(() => {
        resolveCommand()
            .then((command) => {
                props.commandRecognized({ command });
            })
            .catch((error) => {
                props.commandRecognized({ error });
            });
    }, [props.transcript]);

    saveCommand = async (command) => {
        const HISTORY_KEY = 'smart-dom:history';
        const history = JSON.parse(await AsyncStorage.getItem(HISTORY_KEY));
        history.push
  
  const someArray = [1,2,3,4];
  return AsyncStorage.setItem('somekey', JSON.stringify(someArray))
        .then(json => console.log('success!'))
        .catch(error => console.log('error!'));


        try {
            await AsyncStorage.setItem('', 'I like to save it.');
        } catch (error) {
          // Error saving data
        }
      };

    async function resolveCommand() {
        const command = 'command 1234';

        return Promise.resolve('command 1234');
        return Promise.reject('error 1234');
    }

    return (
        <>
            <ActivityIndicator size="large" color={Colors.lightBlue400} />
            <Text>Rozpoznaję polecenie...</Text>
        </>
    );
}

const styles = StyleSheet.create({
});
