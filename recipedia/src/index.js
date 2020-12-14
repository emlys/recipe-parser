import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';


class SearchBar extends React.Component {
    constructor(props) {
        super(props);
        this.state = {value: ''};
    }

    // componentDidMount() {
    //     const search_url = 'http://127.0.0.1:8000/recipedia/search?query=';
    //     fetch(search_url + this.state.query)
    //     .then(res => res.json())
    //     .then();
    // }

    render() {
        console.log('rendering search bar...');

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
    constructor(props) {
        super(props);
        this.state = {value: ''}
    }

    render() {
        return (
            <div className="recipe" id="recipe_container">
                 <h2>Recipe</h2>
            </div>
        )
    }
}


class Recipedia extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            value: ''
        }
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
        console.log(event.target.value);
        this.setState({value: event.target.value});
    }

    handleSubmit(event) {
        console.log('submitted: ' + this.state.value);
        alert('A query was submitted: ' + this.state.value);
        event.preventDefault();
    }

    render() {
        return (
            <div className="page">
                <h1 className="header">Recipedia</h1>
                <SearchBar 
                    value={this.state.value}
                    handleChange={this.handleChange}
                    handleSubmit={this.handleSubmit} />
                <div className="bottom">
                    <Recipe />
                    <h2>Tree</h2>
                </div>
            </div>
        )
    }
}

ReactDOM.render(
  <Recipedia />,
  document.getElementById('root')
);
