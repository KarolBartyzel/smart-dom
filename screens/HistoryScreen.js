import React from 'react';
import { AsyncStorage, FlatList, View, StyleSheet } from 'react-native';
import { ActivityIndicator, Colors, Text } from 'react-native-paper';

export default function HistoryScreen(props) {
    const [history, setHistory] = React.useState(null);

    React.useEffect(() => {
        fetchHistory();
        const focusListener = props.navigation.addListener('didFocus', () => {
            fetchHistory();
        });
        return () => {
            focusListener.remove();
        };
    }, []);

    async function fetchHistory() {
        const HISTORY_KEY = 'smart-dom:history';
        const history = JSON.parse(await AsyncStorage.getItem(HISTORY_KEY)) || [];
        setHistory(history.reverse().map((item, index) => ({ ...item, key: String(index) })));
    }
    
    if (history === null || history === undefined) {
        return (
            <View style={styles.container}>
                <ActivityIndicator size="large" color={Colors.lightBlue400} />
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <FlatList
                contentContainerStyle={styles.list}
                data={history}
                renderItem={({ item, index }) => (
                    <View style={styles.listItem} key={index}>
                        <Text style={styles.listItemCell}>{item.transcript}</Text>
                        <Text style={styles.listItemCell}>{item.command}</Text>
                        <Text style={styles.listItemCell}>{item.date}</Text>
                    </View>
                )}
                ListHeaderComponent={(
                    <View style={styles.listItem}>
                        <Text style={styles.listItemCell}>Mowa</Text>
                        <Text style={styles.listItemCell}>Polecenie</Text>
                        <Text style={styles.listItemCell}>Data</Text>
                    </View>
                )}
                ListEmptyComponent={<View style={styles.container}><Text>Pusta historia</Text></View>}
            />
        </View>
    );
}

HistoryScreen.navigationOptions = {
    header: null
};

const styles = StyleSheet.create({
    container: {
        alignItems: 'center',
        justifyContent: 'center',
    },
    listItem: {
        flexDirection: 'row',
        padding: 10,
        alignItems: 'center',
    },
    listItemCell: {
        width: '33%',
        textAlign: 'center'
    }
});
