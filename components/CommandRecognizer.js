import React from 'react';
import { AsyncStorage, StyleSheet } from 'react-native';
import { Text, ActivityIndicator, Colors } from 'react-native-paper';
import axios from 'axios';
import { SERVER_URL } from './../.env.json';

export default function CommandRecognizer(props) {
    React.useEffect(() => {
        if (props.transcript) {
            resolveCommand()
                .then((command) => {
                    props.finishedRecognition({ command });
                })
                .catch((error) => {
                    props.finishedRecognition({ error });
                });
        }
    }, [props.transcript]);

    saveCommand = async (command) => {
        const HISTORY_KEY = 'smart-dom:history';
        const history = JSON.parse(await AsyncStorage.getItem(HISTORY_KEY)) || [];
        history.push({ date: new Date().toLocaleString(), command, transcript: props.transcript });
        return AsyncStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    };

    async function resolveCommand() {
        return new Promise((resolve, reject) => {
            axios.post(`${SERVER_URL}/command`, {
                transcript: props.transcript
            })
                .then((response) => {
                    const { command } = response.data;
                    if (command !== null) {
                        saveCommand(command);
                        resolve(command);
                    }
                    reject('Polecenie nierozpoznane')
                })
                .catch((error) =>{
                    reject(error);
                });
        });
    }

    if (!props.show) {
        return null;
    }

    return (
        <>
            <ActivityIndicator size="large" color={Colors.orange400} />
            <Text>Rozpoznaję polecenie...</Text>
        </>
    );
}

const styles = StyleSheet.create({
});
