import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

import RecipeTree from './tree.jsx';




class SearchBar extends React.Component {
    constructor(props) {
        super(props);
        this.state = {value: ''};
    }

    render() {
        return (
            <form className="search-container" onSubmit={ this.props.handleSubmit }>
            
                <input 
                    id="search_bar" 
                    className="search-bar"
                    type="text" 
                    value={this.props.value} 
                    placeholder="Search for a food, like mac 'n cheese..."
                    onChange={this.props.handleChange} 
                />
                <button className="search-submit" type="submit">
                    <i className="material-icons mdc-button__icon" 
                       aria-hidden="true">search</i>
                </button>
            </form>
        )
    }
}

class Recipe extends React.Component {

    render() {
        console.log(this.props)
        const steps = this.props.steps.map(
            (step, index) => <li key={index}>{step}</li>);
        console.log('steps:');
        console.log(steps);
        return (
            <div className="recipe" id="recipe_container">
                 <h3>Recipe</h3>
                 <ul>{steps}</ul>
            </div>
        )
    }
}


class Tree extends React.Component {

    render() {
       return <RecipeTree />
        
    }
}


class Recipedia extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            value: '',
            nodes: [],
            steps: []
        }
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
        this.setState({value: event.target.value});
    }

    handleSubmit(event) {
        event.preventDefault();

        const search_url = 'http://127.0.0.1:8000/recipedia/search?query=';
        fetch(search_url + this.state.value)
        .then(res => res.json())
        .then(json => {
            this.setState({'nodes': json.recipe});
            const steps = json.recipe.map((item) => item.instruction);
            this.setState({'steps': steps});
        });
    }

    render() {
        return (
            <div className="page">
                <h1 className="header">Recipedia</h1>
                <h2>a recipe synthesizer</h2>
                <SearchBar 
                    value={this.state.value}
                    handleChange={this.handleChange}
                    handleSubmit={this.handleSubmit} />
                <div className="bottom">
                    <Recipe 
                        steps={this.state.steps}/>
                    <RecipeTree
                        nodes={this.state.nodes}/>
                </div>
            </div>
        )
    }
}

ReactDOM.render(
  <Recipedia />,
  document.getElementById('root')
);
