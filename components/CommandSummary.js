import React from 'react';
import { StyleSheet } from 'react-native';
import { Text, Button } from 'react-native-paper';
import * as Speech from 'expo-speech';
import { GOOGLE_URL } from './../.env.json';

async function synthesizeSpeech(text) {
    // const { uri } = await FileSystem.downloadAsync(
    //     `${GOOGLE_URL}/textToSpeech?text=${encodeURIComponent(text)}`,
    //     `${FileSystem.documentDirectory}synthesizedSpeechTmp.mp3`
    // );
    // const soundObject = new Audio.Sound();
    // try {
    //     await soundObject.loadAsync({ uri });
    //     await soundObject.playAsync();
    // } catch (error) {}
    Speech.speak(text, {
        language: 'pl',
    });
}

export default function CommandSummary(props) {
    const summary = props.error ? `Coś poszło nie tak:\n\n"${props.error}"` : props.command === null ? `Transkrypcja nie została rozpoznana\n\n"${props.transcript}"` : `Transkrypcja została rozpoznana:\n\n"${props.transcript}"\n\nKomenda została wykonana:\n\n"${props.command}"`;
    React.useEffect(() => {
        synthesizeSpeech(summary);
    }, []);
    
    return (
        <>
            <Text style={styles.summary}>{summary}</Text>
            <Button style={styles.button} mode="contained" onPress={props.startNewCommand}>Wydaj nowe polecenie</Button>
        </>
    );
}

const styles = StyleSheet.create({
    button: {
        margin: 10
    },
    summary: {
        textAlign: 'center'
    }
});
