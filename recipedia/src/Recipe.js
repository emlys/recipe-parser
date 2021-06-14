import './index.css';
import React, { useState, useCallback } from 'react';

import Step from './Step.js';
import Ingredient from './Ingredient.js';
import IngredientsGraph from './IngredientsGraph';
import MeasuredDiv from './MeasuredDiv';

var Connector = require('paths-js/connector');

const spacer = '   .'.repeat(500);


// window size controls text position
// ingredient and step text position controls position of nodes
// node position controls position of edges


class Recipe extends React.Component {

  constructor(props) {
    super(props);
    this.testref = React.createRef();
    this.state = {
      bboxMap: {},
      isBold: Object.keys(props.ingredients).reduce((acc, key) => {
        acc[key] = false;
        return acc;
      }, {}),

    };

    this.updateBBox = this.updateBBox.bind(this);
    this.onLabelMouseEnter = this.onLabelMouseEnter.bind(this);
    this.onLabelMouseLeave = this.onLabelMouseLeave.bind(this);
  }

  updateBBox(bbox, index) {
    const bboxMap = this.state.bboxMap;
    bboxMap[index] = bbox;
    this.setState({bboxMap: bboxMap});
  }

  onLabelMouseEnter(key) {
    const isBold = this.state.isBold;
    isBold[key] = true;
    this.setState({isBold: isBold});
  }

  onLabelMouseLeave(key) {
    const isBold = this.state.isBold;
    isBold[key] = false;
    this.setState({isBold: isBold});
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
      isBold
    } = this.state;


    const idToBox = {}
    let boxID = 0;

    let ingredientDivs = [];

    for (const index of ingredients) {
      const ingredient = graph[index];
      idToBox[index] = 'b' + boxID;
      const mdiv = (
        <MeasuredDiv
          updateFunc={this.updateBBox}
          updateDeps={[windowSize]}
          index={'b' + boxID}
          content={
            <Ingredient
              magnitude={ingredient.magnitude}
              unit={ingredient.unit}
              name={ingredient.name}
              isBold={isBold[index]}
            />
          }
        />
      );
      ingredientDivs.push(mdiv);
      boxID += 1;
    }

    // measured box determines node position


    const textOrder = steps.sort((a, b) => a - b);

    let stepDivs = [];
    let stepSpans = [];
    // Group recipe sentences together so that each
    // group has no more than one step
    let boxIDToGroup = {};
    if (Object.keys(graph).length) {
      const step = graph[textOrder[0]]
      let tokens = {}
      for (let index = step.start_index; index <= step.end_index; index++) {
        tokens[index] = fullText[index]
      }
      stepSpans = [(
        <Step
          tokens={tokens}
          verbIndex={step.verb_index}
          labels={step.labeled_ingredients}
          onMouseEnterLabel={this.onLabelMouseEnter}
          onMouseLeaveLabel={this.onLabelMouseLeave} />
      )];

      for (const key of textOrder.slice(1)) {

        idToBox[key] = 'b' + boxID;
        const step = graph[key];

        if (step.parents) { // a node
          stepDivs.push(
            <MeasuredDiv
              index={'b' + boxID}
              updateFunc={this.updateBBox}
              updateDeps={[windowSize]}
              content={stepSpans}
              className="step" />
          );
          let tokens = {}
          for (let index = step.start_index; index <= step.end_index; index++) {
            tokens[index] = fullText[index]
          }
          stepSpans = [(
            <Step
              tokens={tokens}
              verbIndex={step.verb_index}
              labels={step.labeled_ingredients}
              onMouseEnterLabel={this.onLabelMouseEnter}
              onMouseLeaveLabel={this.onLabelMouseLeave} />
          )];
          boxID += 1;

        } else {  // extra info
          let tokens = {}
          for (let index = step.start_index; index <= step.end_index; index++) {
            tokens[index] = fullText[index]
          }
          stepSpans.push(
            <Step
              tokens={tokens}
              verbIndex={step.verb_index}
              labels={step.labeled_ingredients}
              onMouseEnterLabel={this.onLabelMouseEnter}
              onMouseLeaveLabel={this.onLabelMouseLeave} />
          );
        }
      }
      stepDivs.push(
        <MeasuredDiv
          index={'b' + boxID}
          updateFunc={this.updateBBox}
          updateDeps={[windowSize]}
          content={stepSpans}
          className="step" />
      );
    }


    // scale the spacing between nodes to fit the window width
    const horizontalSpacing = bboxMap['svg'] ? bboxMap['svg'].width / (stepDivs.length + 1) : 10;

    const boxIDToCoords = {};
    let x_coord, y_coord;
    // set coordinates for each ingredient node
    let i = 0;
    for (const key of ingredients) {
      const boxID = idToBox[key];
      if (!bboxMap[boxID]) {
        continue;
      }
      x_coord = 10;
      y_coord = (bboxMap[boxID].top - bboxMap['b0'].top +
        (bboxMap[boxID].height / 2));

      boxIDToCoords[boxID] = [x_coord, y_coord];
      i = i + 1;
    }

    // set coordinates for each step node
    x_coord = horizontalSpacing;
    for (const key of steps) {
      const boxID = idToBox[key];
      if (!bboxMap[boxID]) {
        continue;
      }
      y_coord = (bboxMap[boxID].top - bboxMap['b0'].top +
        (bboxMap[boxID].height / 2));

      boxIDToCoords[boxID] = [x_coord, y_coord];
      x_coord += horizontalSpacing;
      i = i + 1
    }

    // make a svg for each node
    const nodes = Object.keys(boxIDToCoords).map(key => {
      return (
          <circle
            fill="white"
            stroke="black"
            r="6"
            cx={boxIDToCoords[key][0]}
            cy={boxIDToCoords[key][1]} />
        );
    });

    // for each node, make a connector from it to each of its parents
    // accumulate all the connectors into a list
    let edges = [];
    for (const step of steps) {
      const box = idToBox[step];

      const endCoord = boxIDToCoords[box];
      const node = graph[step];

      if (endCoord) {
        for (const parent of node.parents) {
          const startCoord = boxIDToCoords[idToBox[parent]];
          const connector = Connector({
            start: startCoord,
            end: endCoord,
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
    }

    const ings = ingredients.map(ingredient => {
      return graph[ingredient];
    });

    return (
      <React.Fragment>
      <div className="bottom">
        <div className="recipe">
          {ingredientDivs}
          <div className="divider" />
          {stepDivs}
        </div>
        <MeasuredDiv
          index="svg"
          content={
            <svg className="graph-svg">
              {edges.concat(nodes)}
            </svg>
          }
          updateFunc={this.updateBBox}
          updateDeps={windowSize}
          className="graph-div" />
      </div>
      </React.Fragment>
    );
  }
}


export default Recipe;
