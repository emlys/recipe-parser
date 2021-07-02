import './index.css';
import React, { useState, useCallback } from 'react';

import Ingredient from './Ingredient.js';
import MeasuredDiv from './MeasuredDiv';
import RecipeText from './RecipeText2';


var Connector = require('paths-js/connector');


function sliceObject(obj, start, end) {
  const newObj = {};
  for (let i = start; i <= end; i++) {
    newObj[i] = obj[i];
  }
  return newObj;
}


class RecipeNode extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    const {
      id,
      content,
      xCoord,
      yCoord,
      nodeIsBold,
      updateBBox,
      windowSize
    } = this.props;

    return (
      <foreignObject x={xCoord} y={yCoord} width="100" height="100">
        <MeasuredDiv
          xmlns="http://www.w3.org/1999/xhtml"
          index={id}
          content={content}
          className={nodeIsBold ? "bold-graph-box" : "graph-box"}
          updateDeps={windowSize}
          updateFunc={updateBBox} />
      </foreignObject>
    );
  }
}


class RecipeGraph extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      bboxes: {},
      wordIsHovered: {}
    };
    this.onMouseEnterWord = this.onMouseEnterWord.bind(this);
    this.onMouseLeaveWord = this.onMouseLeaveWord.bind(this);
    this.updateBBox = this.updateBBox.bind(this);
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

  updateBBox(id, bbox) {
    console.log('updating bbox', id, bbox)
    const bboxes = this.state.bboxes;
    bboxes[id] = bbox;
    this.setState({bboxes: bboxes});
    console.log('after', bboxes);
  }

  render() {
    const {
      nodes,
      fullText,
      windowSize,
    } = this.props;
    const { bboxes, wordIsHovered } = this.state;
    console.log('wordishovered:', wordIsHovered)




    // this mapping will let us look up attributes by word id
    let words = {};
    for (let wordIndex = 0; wordIndex < fullText.length; wordIndex++) {
      words[wordIndex] = {};
    }

    for (const key of Object.keys(nodes)) {
      if (nodes[key].type === 'step') {
        for (const nodeIdObj of nodes[key].node_ids) {
          for (const tokenIndex of nodeIdObj.tokens) {
            if (words[tokenIndex].compoundWords) {
              nodeIdObj.tokens.forEach(id => words[tokenIndex].compoundWords.add(id))
            } else {
              words[tokenIndex].compoundWords = new Set(nodeIdObj.tokens);
            }

            // make a list of node IDs corresponding to each word
            if (words[tokenIndex].nodeIDs) {
              words[tokenIndex].nodeIDs.push(nodeIdObj.node_id);
            } else {
              words[tokenIndex].nodeIDs = [nodeIdObj.node_id];
            }
          }
        }
        words[nodes[key].verb_index].isVerb = true;

      }
    }

    console.log('words:', words);
    const wordIsBold = {};
    const wordIsUnderlined = {};
    const wordIsItalic = {};
    const nodeIsBold = {};


    for (const key of Object.keys(words)) {
      // Make every word with a node label be italic
      if (words[key] && words[key].nodeIDs) {
        wordIsItalic[key] = true;
      }
      // Make every root verb be bold
      if (words[key] && words[key].isVerb) {
        wordIsBold[key] = true;
      }
    }

    // For every hovered word, if the word has a node label,
    // make the corresponding node be bold
    for (const key of Object.keys(wordIsHovered)) {
      if (wordIsHovered[key] === true && words[key] && words[key].nodeIDs) {
        for (const nodeID of words[key].nodeIDs) {
          nodeIsBold[nodeID] = true;
        }

        wordIsUnderlined[key] = true;
        for (const compoundWordID of words[key].compoundWords) {
          wordIsUnderlined[compoundWordID] = true;
        }
      }
    }

    // for (const key of Object.keys(nodeIsHovered)) {
    //   // If a node is hovered, make its outline bold
    //   if (nodeIsHovered[key] === true) {
    //     nodeIsBold[key] = true;

    //   }
    // }






    let ingredientNodes = [];
    let stepNodes = [];
    for (const node of Object.values(nodes)) {
      if (node.type === 'ingredient') {
        ingredientNodes.push(node);
      }
      else if (node.type === 'step') {
        stepNodes.push(node);
      }
    }



    // scale the spacing between nodes to fit the window width
    const verticalSpacing = 100 //bbox ? bbox.height / (stepNodes.length + 1) : 10;
    const horizontalSpacing = bboxes['svg'] ? bboxes['svg'].width / (ingredientNodes.length + 1) : 10;
    const verticalOffset = 10;
    const horizontalOffset = 100;

    let nodeCoords = {};

    // make a svg for each node
    let circles = [];
    let i = 0;
    console.log('nodeisbold:', nodeIsBold)
    for (const ingredientNode of ingredientNodes) {

      const xCoord = i * horizontalSpacing + horizontalOffset;
      const yCoord = verticalOffset;
      nodeCoords[ingredientNode.id] = {
        xCoord: xCoord,
        yCoord: yCoord
      }

      console.log('isbold:', nodeIsBold[ingredientNode.id])
      circles.push(
        <RecipeNode
          id={ingredientNode.id}
          content={ingredientNode.name}
          nodeIsBold={nodeIsBold[ingredientNode.id]}
          xCoord={xCoord}
          yCoord={yCoord}
          updateBBox={this.updateBBox}
          windowSize={windowSize} />
      );
      i++;
    }

    for (const stepNode of stepNodes) {
      console.log(stepNode);

      const sumParentXCoords = stepNode.parents.reduce(
        (acc, parent) => (acc + nodeCoords[parent].xCoord),
        0
      );
      const maxParentYCoord = stepNode.parents.reduce(
        (acc, parent) => Math.max(acc, nodeCoords[parent].yCoord + (bboxes[parent] ? bboxes[parent].height : 0)),
        0
      );

      const xCoord = sumParentXCoords / stepNode.parents.length;
      const yCoord = maxParentYCoord + verticalOffset + 20;
      nodeCoords[stepNode.id] = {
        xCoord: xCoord,
        yCoord: yCoord
      }

      const content = (
        <RecipeText
          tokens={sliceObject(fullText, stepNode.start_index, stepNode.end_index)}
          isBold={sliceObject(wordIsBold, stepNode.start_index, stepNode.end_index)}
          isItalic={sliceObject(wordIsItalic, stepNode.start_index, stepNode.end_index)}
          isUnderlined={sliceObject(wordIsUnderlined, stepNode.start_index, stepNode.end_index)}
          onMouseEnterWord={this.onMouseEnterWord}
          onMouseLeaveWord={this.onMouseLeaveWord} />);

      circles.push(
        <RecipeNode
          id={stepNode.id}
          content={content}
          nodeIsBold={nodeIsBold[stepNode.id]}
          xCoord={xCoord}
          yCoord={yCoord}
          updateBBox={this.updateBBox}
          windowSize={windowSize} />
      );
    }


    // for each node, make a connector from it to each of its parents
    // accumulate all the connectors into a list
    let edges = [];
    for (const stepNode of stepNodes) {

      let endXCoord = nodeCoords[stepNode.id].xCoord;
      let endYCoord = nodeCoords[stepNode.id].yCoord;

      for (const parentID of stepNode.parents) {
        let startXCoord = nodeCoords[parentID].xCoord;
        let startYCoord = nodeCoords[parentID].yCoord;

        console.log('bboxes:', parentID, bboxes)
        if (bboxes[parentID]) {
          startXCoord = nodeCoords[parentID].xCoord + bboxes[parentID].width / 2;
          startYCoord = nodeCoords[parentID].yCoord + bboxes[parentID].height - 1;
        }
        if (bboxes[stepNode.id]) {
          endXCoord = nodeCoords[stepNode.id].xCoord + bboxes[stepNode.id].width / 2;
          endYCoord = nodeCoords[stepNode.id].yCoord + 1;
        }

        const connector = Connector({
          start: [startXCoord, startYCoord],
          end: [endXCoord, endYCoord],
          tension: 0.1
        });

        edges.push(
          <path
            d={ connector.path.print() }
            fill="none"
            stroke="gray"
            stroke-width={1} />
        );
      }
    }

    return (
      <MeasuredDiv
        index="svg"
        content={
          <svg className="graph-svg">
            {edges}
            {circles}
          </svg>
        }
        updateFunc={this.updateBBox}
        updateDeps={windowSize}
        className="graph-div" />
    );
  }
}


export default RecipeGraph;
