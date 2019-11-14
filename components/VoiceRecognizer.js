import React from 'react';
import { StyleSheet, TouchableOpacity } from 'react-native';
import { Text, IconButton, Button, ActivityIndicator, Colors } from 'react-native-paper';
import * as FileSystem from 'expo-file-system';
import * as Permissions from 'expo-permissions';
import { Audio } from 'expo-av';

import { GOOGLE_URL } from './../.env.json'
import FadeInView from './../components/FadeInView';

const recordingOptions = {
    android: {
        extension: '.m4a',
        outputFormat: Audio.RECORDING_OPTION_ANDROID_OUTPUT_FORMAT_MPEG_4,
        audioEncoder: Audio.RECORDING_OPTION_ANDROID_AUDIO_ENCODER_AAC,
        sampleRate: 44100,
        numberOfChannels: 2,
        bitRate: 128000,
    },
    ios: {
        extension: '.wav',
        audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_HIGH,
        sampleRate: 44100,
        numberOfChannels: 1,
        bitRate: 128000,
        linearPCMBitDepth: 16,
        linearPCMIsBigEndian: false,
        linearPCMIsFloat: false,
    },
};

const audioOptions = {
    allowsRecordingIOS: true,
    interruptionModeIOS: Audio.INTERRUPTION_MODE_IOS_DUCK_OTHERS ,
    playsInSilentModeIOS: true,
    shouldDuckAndroid: true,
    interruptionModeAndroid: Audio.INTERRUPTION_MODE_ANDROID_DUCK_OTHERS,
    playThroughEarpieceAndroid: true,
    staysActiveInBackground: true,
};

export default function VoiceRecognizer(props) {
    const [hasRecordingPermission, setHasRecordingPermission] = React.useState(null);
    const [isRecording, setIsRecording] = React.useState(false);
    const [isRecognizingSpeech, setIsRecognizingSpeech] = React.useState(false);
    const [recording, setRecording] = React.useState(null);

    React.useEffect(() => {
        askForMicrophonePermission();
    }, []);

    async function startRecording() {
        const newRecording = new Audio.Recording();
        setRecording(newRecording);

        try {
            await newRecording.prepareToRecordAsync(recordingOptions);
            setIsRecording(true);
            await newRecording.startAsync();
        } catch (error) {
            stopRecording();
        }
    }

    async function stopRecording() {
        try {
            await recording.stopAndUnloadAsync();
        } catch (error) {}
        setIsRecording(false);
        setIsRecognizingSpeech(true);

        fetchTranscription()
            .then((commandTranscriptions) => {
                if (commandTranscriptions.length === 0) {
                    props.finishedRecognition({ error: 'Nie udało się rozpoznać mowy.' });
                }
                else {
                    const { transcript } = commandTranscriptions[0];
                    props.finishedRecognition({ transcript });
                }
            })
            .catch((error) => {
                props.finishedRecognition({ error: error.message });
            })
            .finally(() => {
                setIsRecognizingSpeech(false);
            });
    }

    async function fetchTranscription() {
        const { uri } = await FileSystem.getInfoAsync(recording.getURI());

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.onload = () => {
                const response = JSON.parse(xhr.response);

                if (xhr.status === 200 && response) {
                    resolve(response);
                }
                else {
                    reject(new Error(response));
                }
            };
            xhr.onerror = (error) => {
                reject(new Error(error));
            };

            xhr.open('POST', `${GOOGLE_URL}/speechToText`);
            xhr.setRequestHeader('Content-Type', 'audio/x-wav');
            xhr.send({ uri });
        });
    }

    async function askForMicrophonePermission() {
        setHasRecordingPermission(null);
        const { status } = await Permissions.askAsync(Permissions.AUDIO_RECORDING);
        if (status === 'granted') {
            await Audio.setAudioModeAsync(audioOptions);
            setHasRecordingPermission(true);
        }
        else {
            setHasRecordingPermission(false);
        }
    }

    if (!props.show) {
        return null;
    }

    if (hasRecordingPermission === null) {
        return (
            <>
                <ActivityIndicator size="large" color={Colors.lightBlue400} />
                <Text>Proszę o dostęp do mikrofonu...</Text>
            </>
        );
    }

    if (hasRecordingPermission === false) {
        return (
            <>
                <Text>Aplikacja nie może działać bez dostępu do mikrofonu.</Text>
                <Button mode="contained" onPress={askForMicrophonePermission}>Udostępnij mikrofon</Button>
            </>
        );
    }

    if (isRecognizingSpeech) {
        return (
            <>
                <ActivityIndicator size="large" color={Colors.lightBlue400} />
                <Text>Rozpoznaję mowę...</Text>
            </>
        );
    }

    if (!isRecording) {
        return (
            <React.Fragment>
                <TouchableOpacity style={styles.iconButtonWrapper} onPress={startRecording}>
                    <IconButton
                        icon="mic"
                        size={45}
                        style={styles.icon}
                    />
                    <Text style={styles.label}>Wydaj nowe polecenie</Text>
                </TouchableOpacity >
   
            </React.Fragment>
        );
    }

    if (isRecording) {
        return (
            <React.Fragment>
                <TouchableOpacity style={styles.iconButtonWrapper} onPress={stopRecording}>
                    <FadeInView>
                        <IconButton
                            icon="mic-off"
                            size={45}
                            style={styles.icon}
                        />
                    </FadeInView>
                    <Text style={styles.label}>Zakończ</Text>
                </TouchableOpacity>
            </React.Fragment>
        );
    }
}

const styles = StyleSheet.create({
    label: {
        margin: 20,
    },
    icon: {},
    iconButtonWrapper: {
        alignItems: 'center'
    }
});
