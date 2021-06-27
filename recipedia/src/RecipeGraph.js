import './index.css';
import React from 'react';

import MeasuredDiv from './MeasuredDiv';
var Connector = require('paths-js/connector');


class Span extends React.Component {
  render() {
    const {
      id,
      text,
      isBold,
      isUnderlined,
      isItalic,
      highlightColor,
      onMouseEnter,
      onMouseLeave
    } = this.props;

    console.log('text:', text)
    return (
      <span
        style={{
          fontWeight: (isBold ? 'bold' : ''),
          textDecoration: (isUnderlined ? 'underline' : ''),
          fontStyle: (isItalic ? 'italic' : ''),
          backgroundColor: highlightColor,
          whiteSpace: 'pre'}}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}>
          {text}
      </span>
    );
  }
}


class RecipeGraph extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      bbox: undefined
    };
    this.updateBBox = this.updateBBox.bind(this);
  }

  updateBBox(bbox) {
    this.setState({bbox: bbox});
  }

  render() {
    const {
      nodes,
      windowSize,
      isBold,
      onMouseEnterNode,
      onMouseLeaveNode
    } = this.props;
    const { bbox } = this.state;

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
    const verticalSpacing = bbox ? bbox.height / (stepNodes.length + 1) : 10;
    const horizontalSpacing = bbox ? bbox.width / (ingredientNodes.length + 1) : 10;
    const verticalOffset = 10;
    const horizontalOffset = 10;

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
        <circle
          fill="white"
          stroke="black"
          r="6"
          stroke-width={isBold[ingredientNode.id] ? 3 : 1}
          cx={xCoord}
          cy={yCoord}
          onMouseEnter={() => onMouseEnterNode(ingredientNode.id)}
          onMouseLeave={() => onMouseLeaveNode(ingredientNode.id)} />
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

      const xCoord = sumParentXCoords / stepNode.parents.length + horizontalOffset;
      const yCoord = (i + 1) * verticalSpacing + verticalOffset;
      nodeCoords[stepNode.id] = {
        xCoord: xCoord,
        yCoord: yCoord
      }

      circles.push(
        <circle
          fill="white"
          stroke="black"
          r="6"
          stroke-width={isBold[stepNode.id] ? 3 : 1}
          cx={xCoord}
          cy={yCoord}
          onMouseEnter={() => onMouseEnterNode(stepNode.id)}
          onMouseLeave={() => onMouseLeaveNode(stepNode.id)} />
      );

      i++;
    }

    console.log('circles:', circles);

    // for each node, make a connector from it to each of its parents
    // accumulate all the connectors into a list
    let edges = [];
    for (const stepNode of stepNodes) {

      const endXCoord = nodeCoords[stepNode.id].xCoord;
      const endYCoord = nodeCoords[stepNode.id].yCoord;

      for (const parentID of stepNode.parents) {
        const startXCoord = nodeCoords[parentID].xCoord;
        const startYCoord =  nodeCoords[parentID].yCoord;

        const connector = Connector({
          start: [startXCoord, startYCoord],
          end: [endXCoord, endYCoord],
          tension: 0.1
        });

        edges.push(
          <path
            d={ connector.path.print() }
            fill="none"
            stroke="gray" />
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
