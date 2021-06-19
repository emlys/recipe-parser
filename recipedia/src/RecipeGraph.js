import './index.css';
import React from 'react';

import MeasuredDiv from './MeasuredDiv';


class RecipeGraph extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      bboxMap: {}
    };
    this.updateBBox = this.updateBBox.bind(this);
  }

  updateBBox(bbox, index) {
    const bboxMap = this.state.bboxMap;
    bboxMap[index] = bbox;
    this.setState({bboxMap: bboxMap});
  }


  render() {
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

    return (
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
    );
  }
}

export default RecipeGraph;
