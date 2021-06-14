import './index.css';
import React, { useState, useCallback } from 'react';


class IngredientsGraph extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            isClicked: props.ingredients.map(i => false)
        }
        this.onSectionClick = this.onSectionClick.bind(this);
    }

    onSectionClick(index) {
        console.log('toggling index', index);
        const isClicked = this.state.isClicked;
        isClicked[index] = !isClicked[index];
        this.setState({isClicked: isClicked});
    }

    render() {
        const {
            ingredients
        } = this.props;

        const {
            isClicked
        } = this.state;
        console.log('isclicked', isClicked);

        const [r_min, g_min, b_min] = [30, 33, 72];
        const [r_max, g_max, b_max] = [248, 173, 6];

        const [r_gap, g_gap, b_gap] = [
            (r_max - r_min) / ingredients.length,
            (g_max - g_min) / ingredients.length,
            (b_max - b_min) / ingredients.length
        ]
        console.log('gaps:', r_gap, g_gap, b_gap);

        let bar = [];
        let i = 0;
        for (const ingredient of ingredients.sort((a, b) => b.magnitude - a.magnitude)) {
            console.log('iii', isClicked[i], (isClicked[i] ? '2px solid white' : '0.5px solid white'));
            const a = i;
            bar.push(
                <div 
                    style={{
                        height: ingredient.magnitude * 20, 
                        width: '300px',
                        backgroundColor: `rgb(${r_min + r_gap * i}, ${g_min + g_gap * i}, ${b_min + b_gap * i})`,
                        border: isClicked[i] ? '2px solid white' : '0.5px solid white'}}
                    onClick={event => {
                        this.onSectionClick(a);
                    }}
                />)
            i += 1;
        }

        return (
            <div className="ingredients-bar">
                {bar}
            </div>
        )

    }
}

export default IngredientsGraph;
