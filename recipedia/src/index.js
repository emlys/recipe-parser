import React, { useCallback } from 'react';
import ReactDOM from 'react-dom';
import './index.css';

import Recipe from './tree.jsx';




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





class Recipedia extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            value: '',
            steps: [],
            ingredients: [],
            width: window.innerWidth,
            height: window.innerHeight,
            coord: 0
        }
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.updateDimensions = this.updateDimensions.bind(this);
    }

    componentDidMount() {
      window.addEventListener('resize', this.updateDimensions);
    }

    updateDimensions() {
      this.setState({width: window.innerWidth, height: window.innerHeight});
    }

    handleChange(event) {
        this.setState({value: event.target.value});
    }

    handleSubmit(event) {
        event.preventDefault();
        console.log('handle submit');

        const search_url = 'http://127.0.0.1:8000/recipedia/search?query=';
        fetch(search_url + this.state.value)
        .then(res => res.json())
        .then(json => {
            console.log('json:', json);
            console.log(json.ingredients);
            console.log(json.steps);
            let nodeMap = {};
            const nodes = json.graph;
            console.log('nodes:', nodes);
            for (const node of nodes) {
                console.log(node.name, node);
                nodeMap[node.name] = node;
            }
            this.setState({
                'ingredients': json.ingredients,
                'graph': json.graph,
                'nodeMap': nodeMap });
        });
    }

    render() {
        console.log('state:', this.state);
        return (
            <div className="page">
                <h1 className="header">Recipedia</h1>
                <h2>a recipe synthesizer</h2>
                <SearchBar 
                    value={this.state.value}
                    handleChange={this.handleChange}
                    handleSubmit={this.handleSubmit} />
                <Recipe 
                    position={[0, 0]}
                    height={this.state.ingredients.length * 20}
                    ingredients={this.state.ingredients}
                    graph={this.state.graph || []}
                    nodeMap={this.state.nodeMap}
                    windowSize={[this.state.width, this.state.height]} />
            </div>
        )
    }
}

ReactDOM.render(
  <Recipedia />,
  document.getElementById('root')
);
