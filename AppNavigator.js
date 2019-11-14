import React from 'react';
import { createAppContainer, createSwitchNavigator, createStackNavigator, createBottomTabNavigator } from 'react-navigation';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';

import Colors from './constants/Colors';
import OrdersScreen from './screens/OrdersScreen';
import DevicesScreen from './screens/DevicesScreen';
import HistoryScreen from './screens/HistoryScreen';

const OrdersStack = createStackNavigator(
    {
        Orders: OrdersScreen,
    }
);

OrdersStack.navigationOptions = {
    tabBarLabel: 'Polecenia',
    tabBarIcon: ({ focused }) => (
        <Ionicons
            name={'md-microphone'}
            size={26}
            style={{ marginBottom: -3 }}
            color={focused ? Colors.tabIconSelected : Colors.tabIconDefault}
        />
    ),
};

OrdersStack.path = '';

const DevicesStack = createStackNavigator(
    {
        Devices: DevicesScreen,
    },
);

DevicesStack.navigationOptions = {
    tabBarLabel: 'Urządzenia',
    tabBarIcon: ({ focused }) => (
        <MaterialCommunityIcons
            name={'floor-plan'}
            size={26}
            style={{ marginBottom: -3 }}
            color={focused ? Colors.tabIconSelected : Colors.tabIconDefault}
        />
    ),
};

DevicesStack.path = '';

const HistoryStack = createStackNavigator(
    {
        History: HistoryScreen,
    },
);

HistoryStack.navigationOptions = {
    tabBarLabel: 'Historia',
    tabBarIcon: ({ focused }) => (
        <MaterialCommunityIcons
            name={'history'}
            size={26}
            style={{ marginBottom: -3 }}
            color={focused ? Colors.tabIconSelected : Colors.tabIconDefault}
        />
    ),
};

HistoryStack.path = '';

const tabNavigator = createBottomTabNavigator({
    OrdersStack,
    HistoryStack,
    // DevicesStack,
});

tabNavigator.path = '';

export default createAppContainer(
    createSwitchNavigator({
        Main: tabNavigator,
    })
);
