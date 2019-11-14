import React from 'react';
import { View } from 'react-native';
import { Text } from 'react-native-paper';

export default function DevicesScreen(props) {
    return (
        <View>
            <Text>Urządzenia</Text>
        </View>
    )
}

DevicesScreen.navigationOptions = {
    header: null
};
