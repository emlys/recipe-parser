import './index.css';
import React, { useState, useCallback } from 'react';

import Ingredient from './Ingredient.js';
import MeasuredDiv from './MeasuredDiv';
import RecipeGraph from './RecipeGraph.js';
import RecipeText from './RecipeText.js';

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
      nodeIsHovered: Object.keys(props.graph).reduce((acc, key) => {
        acc[key] = false;
        return acc;
      }, {}),
    };

    this.updateBBox = this.updateBBox.bind(this);
    this.onMouseEnterWord = this.onMouseEnterWord.bind(this);
    this.onMouseLeaveWord = this.onMouseLeaveWord.bind(this);
    this.onMouseEnterNode = this.onMouseEnterNode.bind(this);
    this.onMouseLeaveNode = this.onMouseLeaveNode.bind(this);
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

  onMouseEnterNode(key) {
    const nodeIsHovered = this.state.nodeIsHovered;
    nodeIsHovered[key] = true;
    this.setState({nodeIsHovered: nodeIsHovered});
  }

  onMouseLeaveNode(key) {
    const nodeIsHovered = this.state.nodeIsHovered;
    nodeIsHovered[key] = false;
    this.setState({nodeIsHovered: nodeIsHovered});
  }

  render() {
    const {
      graph,
      fullText,
      windowSize
    } = this.props;

    const {
      bboxMap,
      wordIsHovered,
      nodeIsHovered
    } = this.state;



    let words = {};
    for (let wordIndex = 0; wordIndex < fullText.length; wordIndex++) {
      words[wordIndex] = {};
    }

    for (const key of Object.keys(graph)) {
      if (graph[key].type === 'step') {
        for (const nodeIdObj of graph[key].node_ids) {
          for (const tokenIndex of nodeIdObj.tokens) {
            words[tokenIndex].compoundWords = nodeIdObj.node_id;

            if (words[tokenIndex].ingredientIDs) {
              words[tokenIndex].ingredientIDs.push(nodeIdObj.node_id);
            } else {
              words[tokenIndex].ingredientIDs = [nodeIdObj.node_id];
            }
          }
        }
        words[graph[key].verb_index].isVerb = true;

      }
    }

    console.log('words:', words);
    let wordIsBold = {};
    let wordIsUnderlined = {};
    let wordIsItalic = {};
    let wordHighlightColor = {};
    let ingredientIsBold = {};
    let nodeIsBold = {};

    // Make every word with an ingredient label be bold
    for (const key of Object.keys(words)) {
      if (words[key] && words[key].ingredientIDs) {
        wordIsBold[key] = true;
      }
      if (words[key] && words[key].isVerb) {
        wordIsItalic[key] = true;
      }
    }

    // for (const key of Object.keys(graph)) {
    //   for (let wordIndex = graph[key].start_index; wordIndex <= graph[key].end_index; wordIndex++) {
    //     console.log('highlighting word', wordIndex)
    //     wordHighlightColor[wordIndex] = 'rgba(220, 50, 183, 0.34)';
    //   }
    // }

    // For every hovered word, if the word has an ingredient label,
    // make the corresponding ingredient be bold
    for (const key of Object.keys(wordIsHovered)) {
      if (wordIsHovered[key] === true && words[key] && words[key].ingredientIDs) {
        for (const ingredientID of words[key].ingredientIDs) {
          ingredientIsBold[ingredientID] = true;
        }

        wordIsUnderlined[key] = true;
        for (const compoundWordID of words[key].compoundWords) {
          wordIsUnderlined[compoundWordID] = true;
        }
      }
    }

    for (const key of Object.keys(nodeIsHovered)) {
      // If a node is hovered, make its outline bold
      if (nodeIsHovered[key] === true) {
        nodeIsBold[key] = true;


        for (let wordIndex = graph[key].start_index; wordIndex <= graph[key].end_index; wordIndex++) {
          console.log('highlighting word', wordIndex)
          wordHighlightColor[wordIndex] = 'rgba(220, 50, 183, 0.34)';
        }
      }
    }

    let ingredientDivs = [];

    for (const index of Object.keys(graph)) {
      if (graph[index].type === 'ingredient') {
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
    }

    console.log('highlights:', wordHighlightColor)
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
            highlightColor={wordHighlightColor}
            onMouseEnterWord={this.onMouseEnterWord}
            onMouseLeaveWord={this.onMouseLeaveWord} />
        </div>
        <RecipeGraph
          nodes={graph}
          isBold={nodeIsBold}
          windowSize={windowSize}
          onMouseEnterNode={this.onMouseEnterNode}
          onMouseLeaveNode={this.onMouseLeaveNode} />
      </div>
      </React.Fragment>
    );
  }
}


export default Recipe;
