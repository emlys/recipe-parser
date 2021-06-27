import React, { useCallback } from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Route, Link } from 'react-router-dom';
import './index.css';

import Recipe from './Recipe2.js';
import About from './about.js';


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


class Footer extends React.Component {

    render() {
        return (
            <div className="footer">
                <Link to="/about" className="footer-item">About</Link>
                <a
                    target="_blank"
                    rel="noopener noreferrer"
                    href="https://github.com/emlys/recipe-parser"
                    className="footer-item">GitHub</a>
                <Link to="/" className="footer-item">Contact</Link>
            </div>
        );
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

        const search_url = 'http://127.0.0.1:8000/recipedia/search?query=';
        fetch(search_url + this.state.value)
        .then(res => res.json())
        .then(json => {
            this.setState({
                graph: json.nodes,
                fullText: json.full_text
            });
        });
    }

    render() {
        console.log('rendering main page');
        let recipe = null;

        if (this.state.graph) {
            recipe = (
                <Recipe
                    graph={this.state.graph || []}
                    windowSize={[this.state.width, this.state.height]}
                    fullText={this.state.fullText} />
            );
        }

        const page = (
            <div className="page">
                <h1 className="header">Recipedia</h1>
                <h2>a recipe synthesizer</h2>
                <SearchBar
                    value={this.state.value}
                    handleChange={this.handleChange}
                    handleSubmit={this.handleSubmit} />
                {recipe}
                <Footer />
            </div>
        );

        return (
            page
        );


    }
}


export default function App() {
  return (
   <BrowserRouter>


        <Route path="/" exact component={Recipedia} />
        <Route path="/about"  component={About} />

    </BrowserRouter>
  );
}


