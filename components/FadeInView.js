import React from 'react';
import { Animated } from 'react-native';

function FadeInView(props) {
    const [fadeAnimation, setFadeAnimation] = React.useState(new Animated.Value(0));

    React.useEffect(() => {
        Animated.loop(Animated.timing(fadeAnimation, { toValue: 1, duration: 1400, })).start();
    }, []);

    return (
        <Animated.View style={{ opacity: fadeAnimation }}>
            {props.children}
        </Animated.View>
    )
}

export default FadeInView;
