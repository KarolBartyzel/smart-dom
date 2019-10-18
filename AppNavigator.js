import React from 'react';
import { createAppContainer, createSwitchNavigator, createStackNavigator, createBottomTabNavigator } from 'react-navigation';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';

import Colors from './constants/Colors';
import OrdersScreen from './screens/OrdersScreen';
import DevicesScreen from './screens/DevicesScreen';

const OrdersStack = createStackNavigator(
    {
        Orders: OrdersScreen,
    }
);

OrdersStack.navigationOptions = {
    tabBarLabel: 'Rozkazy',
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

const tabNavigator = createBottomTabNavigator({
    OrdersStack,
    DevicesStack,
});

tabNavigator.path = '';

export default createAppContainer(
    createSwitchNavigator({
        Main: tabNavigator,
    })
);
