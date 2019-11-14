import React from 'react';
import { StyleSheet, View } from 'react-native';

import VoiceRecognizer from './../components/VoiceRecognizer';
import CommandRecognizer from './../components/CommandRecognizer';
import CommandSummary from './../components/CommandSummary';

export default function OrderScreen(props) {
    const [transcript, setTranscript] = React.useState(null);
    const [command, setCommand] = React.useState(null);
    const [error, setError] = React.useState(null);

    function finishedVoiceRecognition({ error, transcript }) {
        if (transcript) {
            setTranscript(transcript);
        }
        if (error) {
            setError(error);
        }
    }

    function finishedCommandRecognition({ error, command }) {
        if (command) {
            setCommand(command);
        }
        if (error) {
            setError(error);
        }
    }

    function startNewCommand() {
        setTranscript(null);
        setCommand(null);
        setError(null);
    }

    return (
        <View style={styles.container}>
            {<VoiceRecognizer show={!error && !transcript} finishedRecognition={finishedVoiceRecognition} />}
            {<CommandRecognizer show={!error && transcript && !command} transcript={transcript} finishedRecognition={finishedCommandRecognition} />}
            {(error || (transcript && command)) && <CommandSummary transcript={transcript} command={command} error={error} startNewCommand={startNewCommand} />}
        </View>
    );
}

OrderScreen.navigationOptions = {
    header: null,
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        backgroundColor: '#fff',
    },
});
