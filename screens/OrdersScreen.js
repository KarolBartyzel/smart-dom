import React, { Fragment, useState } from 'react';
import { StyleSheet, View } from 'react-native';
import { Text, IconButton, ActivityIndicator } from 'react-native-paper';
import * as Permissions from 'expo-permissions';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import * as Speech from 'expo-speech';
import { GOOGLE_URL } from 'react-native-dotenv'

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

export default function HomeScreen() {
    const [audioRecordingPermission, setAudioRecordingPermission] = useState(null);
    const [recording, setRecording] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [isFetchingTranscription, setIsFetchingTranscription] = useState(false);
    const [isResolvingCommand, setIsResolvingCommand] = useState(false);
    const [successfulCommand, setSuccessfulCommand] = useState(null);
    const [failedCommand, setFailedCommand] = useState(null);

    React.useEffect(() => {
        askForMicrophonePermission();
    }, []);

    async function askForMicrophonePermission() {
        const { status } = await Permissions.askAsync(Permissions.AUDIO_RECORDING);
        await Audio.setAudioModeAsync(audioOptions);
        setAudioRecordingPermission(status === "granted");
        return status === "granted";
    }

    async function startRecording() {
        if (!audioRecordingPermission && !askForMicrophonePermission()) {
            return;
        }
        setSuccessfulCommand(null);
        setFailedCommand(null);
        const recording = new Audio.Recording();
        setRecording(recording);

        try {
            await recording.prepareToRecordAsync(recordingOptions);
            setIsRecording(true);
            await recording.startAsync();
        } catch (error) {
            stopRecording();
        }
    }

    async function stopRecording() {
        setIsFetchingTranscription(true);
        setIsRecording(false);
        try {
            await recording.stopAndUnloadAsync();
        } catch (error) {}

        fetchTranscription()
            .then((commandTranscriptions) => {
                return resolveCommand(commandTranscriptions)
                    .then((command) => {
                        setSuccessfulCommand(command);
                        synthesizeSpeech(command);
                    });
            })
            .catch((error) => {
                setFailedCommand(error.message);
                synthesizeSpeech(error.message);
            });
    }

    async function fetchTranscription() {
        const { uri } = await FileSystem.getInfoAsync(recording.getURI());

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.onload = () => {
                setIsFetchingTranscription(false);
                const response = JSON.parse(xhr.response);

                if (xhr.status === 200 && response) {
                    setIsResolvingCommand(true);
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

    async function resolveCommand(commandTranscriptions) {
        const { transcript, confidence } = commandTranscriptions[0];
        setIsResolvingCommand(false);
        return Promise.resolve(`Komenda "${transcript}" wykonana pomyślnie`);
        const failedCommand = "Blabla";
        return Promise.reject(`Komenda nie została rozpoznana. Powód: "${failedCommand}".`);
    }

    return (
        <View style={styles.container}>
            {!isFetchingTranscription && !isResolvingCommand && (
                <Fragment>
                    {successfulCommand && (
                        <Text style={styles.header}>{successfulCommand}</Text>
                    )}
                    {failedCommand && (
                        <Text style={styles.header}>{failedCommand}</Text>
                    )}
                    {!isRecording && (
                        <Fragment>
                            <Text style={styles.header}>Naciśnij aby wydać nowe polecenie</Text>
                            <IconButton
                                icon="mic"
                                size={45}
                                style={styles.icon}
                                onPress={startRecording}
                            />
                        </Fragment>
                    )}
                </Fragment>
            )}
            {isRecording && (
                <Fragment>
                    <Text style={styles.header}>Naciśnij aby zakończyć wydawanie polecenia</Text>
                    <FadeInView>
                        <IconButton
                            icon="mic-off"
                            size={45}
                            style={styles.icon}
                            onPress={stopRecording}
                        />
                    </FadeInView>
                </Fragment>
            )}
            {(isFetchingTranscription || isResolvingCommand) && (
                <Fragment>
                    <Text style={styles.header}>Polecenie jest rozpoznawane, proszę czekać</Text>
                    <ActivityIndicator size="large" animating={true} />
                </Fragment>
            )}
        </View>
    );
}

HomeScreen.navigationOptions = {
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
    header: {
        margin: 20,
    },
    icon: {
    },
});
