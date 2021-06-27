import './index.css';
import React, { useState, useCallback } from 'react';

import Ingredient from './Ingredient.js';
import MeasuredDiv from './MeasuredDiv';
import RecipeText from './RecipeText2';


var Connector = require('paths-js/connector');


class RecipeNode extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      bbox: {}
    };
    this.updateBBox = this.updateBBox.bind(this);

  }

  updateBBox(index, new_bbox) {
    const bbox = this.state.bbox;
    bbox[index] = new_bbox;
    this.setState({bbox: bbox});
  }

  render() {
    const {
      node,
      fullText,
      xCoord,
      yCoord,
      updateBBox,
      windowSize
    } = this.props;

    let words = {};
    for (let wordIndex = 0; wordIndex < fullText.length; wordIndex++) {
      words[wordIndex] = {};
    }

    if (node.type === 'step') {
      for (const nodeIdObj of node.node_ids) {
        for (const tokenIndex of nodeIdObj.tokens) {
          words[tokenIndex].compoundWords = nodeIdObj.node_id;

          if (words[tokenIndex].ingredientIDs) {
            words[tokenIndex].ingredientIDs.push(nodeIdObj.node_id);
          } else {
            words[tokenIndex].ingredientIDs = [nodeIdObj.node_id];
          }
        }
      }
      words[node.verb_index].isVerb = true;
    }

    if (node.type === 'step') {
      const tokens = {};
      for (let key = node.start_index; key <= node.end_index; key++) {
        tokens[key] = fullText[key]
      }
      const isBold = {};
      isBold[node.verb_index] = true;

      return (
        <foreignObject x={xCoord} y={yCoord} width="200" height="200">
          <MeasuredDiv
            xmlns="http://www.w3.org/1999/xhtml"
            index={node.id}
            content={
              <RecipeText
                tokens={tokens}
                isBold={isBold} />
            }
            className="graph-box"
            updateDeps={windowSize}
            updateFunc={updateBBox} />
        </foreignObject>
      );
    } else {
      return (
        <foreignObject x={xCoord} y={yCoord} width="100" height="100">
          <MeasuredDiv
            xmlns="http://www.w3.org/1999/xhtml"
            index={node.id}
            content={node.name}
            className="graph-box"
            updateDeps={windowSize}
            updateFunc={updateBBox} />
        </foreignObject>
      );
    }
  }
}


class RecipeGraph extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      bboxes: {}
    };
    this.updateBBox = this.updateBBox.bind(this);
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
      isBold,
      onMouseEnterNode,
      onMouseLeaveNode
    } = this.props;
    const { bboxes } = this.state;

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
    for (const ingredientNode of ingredientNodes) {

      const xCoord = i * horizontalSpacing + horizontalOffset;
      const yCoord = verticalOffset;
      nodeCoords[ingredientNode.id] = {
        xCoord: xCoord,
        yCoord: yCoord
      }

      circles.push(
        <RecipeNode
          node={ingredientNode}
          fullText={fullText}
          xCoord={xCoord}
          yCoord={yCoord}
          updateBBox={this.updateBBox}
          windowSize={windowSize} />
      );
      i++;
    }

    i = 0;
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

      const tokens = {};
      for (let key = stepNode.start_index; key <= stepNode.end_index; key++) {
        tokens[key] = fullText[key]
      }
      const isBold = {};
      isBold[stepNode.verb_index] = true;

      circles.push(
        <RecipeNode
          node={stepNode}
          fullText={fullText}
          xCoord={xCoord}
          yCoord={yCoord}
          updateBBox={this.updateBBox}
          windowSize={windowSize} />
      );

      i++;
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


    console.log('highlights:', wordHighlightColor)
    return (
      <React.Fragment>
      <div className="bottom2">
        <RecipeGraph
          nodes={graph}
          fullText={fullText}
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
