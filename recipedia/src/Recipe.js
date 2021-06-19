import './index.css';
import React, { useState, useCallback } from 'react';

import RecipeText from './RecipeText.js';
import Ingredient from './Ingredient.js';
import IngredientsGraph from './IngredientsGraph';
import MeasuredDiv from './MeasuredDiv';

var Connector = require('paths-js/connector');


// window size controls text position
// ingredient and step text position controls position of nodes
// node position controls position of edges


class Recipe extends React.Component {

  constructor(props) {
    super(props);
    this.testref = React.createRef();
    this.state = {
      bboxMap: {},
      wordIsHovered: Object.keys(props.fullText).reduce((acc, key) => {
        acc[key] = false;
        return acc;
      }, {}),
    };

    this.updateBBox = this.updateBBox.bind(this);
    this.onMouseEnterWord = this.onMouseEnterWord.bind(this);
    this.onMouseLeaveWord = this.onMouseLeaveWord.bind(this);
  }

  updateBBox(bbox, index) {
    const bboxMap = this.state.bboxMap;
    bboxMap[index] = bbox;
    this.setState({bboxMap: bboxMap});
  }

  onMouseEnterWord(key) {
    const wordIsHovered = this.state.wordIsHovered;
    wordIsHovered[key] = true;
    this.setState({wordIsHovered: wordIsHovered});
  }

  onMouseLeaveWord(key) {
    const wordIsHovered = this.state.wordIsHovered;
    wordIsHovered[key] = false;
    this.setState({wordIsHovered: wordIsHovered});
  }

  render() {
    const {
      ingredients,
      steps,
      graph,
      windowSize,
      fullText
    } = this.props;

    const {
      bboxMap,
      wordIsHovered
    } = this.state;



    let words = {};
    for (let wordIndex = 0; wordIndex < fullText.length; wordIndex++) {
      words[wordIndex] = {};
    }

    for (const key of Object.keys(graph)) {
      if (graph[key].type === 'step') {
        for (const ingredientID of Object.keys(graph[key].labeled_ingredients)) {
          for (const tokenIndex of graph[key].labeled_ingredients[ingredientID]) {
            words[tokenIndex].compoundWords = graph[key].labeled_ingredients[ingredientID];
            words[tokenIndex].ingredientID = ingredientID;
          }
        }
        words[graph[key].verb_index].isVerb = true;

      }
    }

    console.log('words:', words);
    let wordIsBold = {};
    let wordIsUnderlined = {};
    let wordIsItalic = {};
    let ingredientIsBold = {};

    // Make every word with an ingredient label be bold
    for (const key of Object.keys(words)) {
      if (words[key] && words[key].ingredientID) {
        wordIsBold[key] = true;
      }
      if (words[key] && words[key].isVerb) {
        wordIsItalic[key] = true;
      }
    }

    // For every hovered word, if the word has an ingredient label,
    // make the corresponding ingredient be bold
    for (const key of Object.keys(wordIsHovered)) {
      if (wordIsHovered[key] === true && words[key] && words[key].ingredientID) {
        ingredientIsBold[words[key].ingredientID] = true;

        wordIsUnderlined[key] = true;
        for (const compoundWordID of words[key].compoundWords) {
          wordIsUnderlined[compoundWordID] = true;
        }
      }
    }

    let ingredientDivs = [];

    for (const index of ingredients) {
      const ingredient = graph[index];
      const mdiv = (
        <MeasuredDiv
          updateFunc={this.updateBBox}
          updateDeps={[windowSize]}
          index={'b' + index}
          content={
            <Ingredient
              magnitude={ingredient.magnitude}
              unit={ingredient.unit}
              name={ingredient.name}
              isBold={ingredientIsBold[index]}
            />
          }
        />
      );
      ingredientDivs.push(mdiv);
    }


    return (
      <React.Fragment>
      <div className="bottom">
        <div className="recipe">
          {ingredientDivs}
          <div className="divider" />
          <RecipeText
            tokens={fullText}
            isBold={wordIsBold}
            isUnderlined={wordIsUnderlined}
            isItalic={wordIsItalic}
            onMouseEnterWord={this.onMouseEnterWord}
            onMouseLeaveWord={this.onMouseLeaveWord} />
        </div>
      </div>
      </React.Fragment>
    );
  }
}


export default Recipe;
