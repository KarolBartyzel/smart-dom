import React, { Fragment, useState } from 'react';
import { StyleSheet, View } from 'react-native';
import { Text, IconButton, ActivityIndicator } from 'react-native-paper';
import * as Permissions from 'expo-permissions';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { Buffer } from 'buffer';

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
    interruptionModeIOS: Audio.INTERRUPTION_MODE_IOS_DO_NOT_MIX,
    playsInSilentModeIOS: true,
    shouldDuckAndroid: true,
    interruptionModeAndroid: Audio.INTERRUPTION_MODE_ANDROID_DO_NOT_MIX,
    playThroughEarpieceAndroid: true,
    staysActiveInBackground: false,
};

export default function HomeScreen() {
    const [recording, setRecording] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [isFetchingTranscription, setIsFetchingTranscription] = useState(false);
    const [isResolvingCommand, setIsResolvingCommand] = useState(false);
    const [successfulCommand, setSuccessfulCommand] = useState(null);
    const [failedCommand, setFailedCommand] = useState(null);

    async function askForMicrophonePermission() {
        const { status } = await Permissions.askAsync(Permissions.AUDIO_RECORDING);
        return status === "granted";
    }

    async function startRecording() {
        if (!askForMicrophonePermission()) {
            return;
        }
        setSuccessfulCommand(null);
        setFailedCommand(null);
        await Audio.setAudioModeAsync(audioOptions);
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
                        // Syntezuj mowę
                    });
            })
            .catch((error) => {
                setFailedCommand(error.message);
                // Syntezuj mowę
            });
    }

    async function fetchTranscription() {
        const { uri } = await FileSystem.getInfoAsync(recording.getURI());

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.onload = () => {
                setIsFetchingTranscription(false);
                const { status, response } = xhr;
                console.log(response, status);
                console.log('lala');
                if (status === 200 && response.length > 0) {
                    setIsResolvingCommand(true);
                    resolve(response);
                }
                else {
                    reject(new Error(response));
                }
            };
            xhr.onerror = (error) => {
                reject(new Error(response));
            };

            xhr.open('POST', 'CHANGE');
            xhr.setRequestHeader('Content-Type', 'audio/x-wav');
            xhr.send({ uri });
        });
    }

    async function resolveCommand(commandTranscriptions) {
        console.log(typeof commandTranscriptions);
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
        backgroundColor: '#fff',
    },
    header: {
        margin: 20,
    },
    icon: {
    },
});
