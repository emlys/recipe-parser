import './index.css';
import React, { useState, useCallback } from 'react';


var Bezier = require('paths-js/bezier');


function children(x) {
  return x.parents || []
}

function averageXCoords(array) {
    var sum = array.reduce(function(a, b) {
        return a + b.point[0];
    }, 0);
    // const sum = array.reduce((accumulator, current) => {accumulator + current}, 0);
    return sum / array.length;
}

function numberOfIngredients(nodes) {
    return nodes.reduce((acc, node) => {
        console.log(node.parents.length);
        if (node.parents.length === 0) {
            return acc + 1;
        } else {
            return acc
        }
    }, 0);
}

function mapNamesToNodes(nodes) {
    // mapping from each node name to the node with that name
    let nodeMap = nodes.reduce((map, node) => {
        map.set(node.name, node);
        return map;
    }, new Map());
    return nodeMap;
}


// /**
//  * Calculate pixel coordinates for each node in the tree.
//  * @param nodes: an array of Nodes
//  * @param height: the height in pixels of the whole SVG area
//  * @param width: the width in pixels of the whole SVG area
// */
function setNodeCoords(ingredientNodes, stepNodes, height, width) {

  let nodeMap = new Map();
  // let nodeMap = mapNamesToNodes(nodes);
  // the number of rows in the final tree graph
  // all ingredients go in the first row
  // after that, one row per step
  let xCoord, yCoord;
 
  // const nRows = nodes.length - nIngredients + 1;

  // calculate the horizontal and vertical spacing between nodes
  const xGap = (width - 20) / ingredientNodes.length;
  const yGap = (height - 20) / (stepNodes.length + 1);
  console.log('gaps:', xGap, yGap, height, width, ingredientNodes.length, stepNodes.length)

  let ingredientNodesWithPoints = ingredientNodes.map(
      (node, index) => {
          xCoord = (index * xGap) + 10 ;
          yCoord = 10;
          node.point = [xCoord, yCoord];
          nodeMap.set(node.name, node);
          return node;
      }
  );
  let stepNodesWithPoints = stepNodes.map(
      (node, index) => {
          // evenly space the node horizontally between its parent nodes
          xCoord = averageXCoords(node.parents.map(parent => nodeMap.get(parent)));
          yCoord = (index + 1) * yGap + 10;
          node.point = [xCoord, yCoord];
          nodeMap.set(node.name, node);
          return node;
      }
  );
  return ingredientNodesWithPoints.concat(stepNodesWithPoints);
}

// window size controls text position
// ingredient and step text position controls position of nodes
// node position controls position of edges



// class Ingredient extends React.Component {

//     constructor(props) {
//       super(props);
//       this.ref = React.createRef();
//     }

//     render() {
//         console.log('rendering ingredient');
//         console.log('position', this.props.position)
//         console.log('bounding box:', this.ref.current.getBoundingClientRect());
//         return (
//             <React.Fragment>
//               <foreignObject 
//                   height="20px" 
//                   width="300px"
//                   transform={"translate(0," + this.props.position[1] + ")"}>
//                       <div key={this.props.key}>{this.props.text}</div>
//               </foreignObject>
//               <Node
//                   label={this.props.text}
//                   transform={"translate(300," + (this.props.position[1] + 10) + ")"} />
//             </React.Fragment>
//         );
//     }
// }

function Ingredient(props) {

  console.log('windowsize:', props.windowSize);
  const measuredRef = useCallback(node => {  
    console.log('in callback for ', node);  
    if (node !== null) {
      console.log('calling update func:', node.getBoundingClientRect(), props.index)
      props.updateFunc(node.getBoundingClientRect(), props.index);
    }  
  }, [props.windowSize]);

  console.log('rendering ingredient:', props);
  return (
    <React.Fragment>
    <div key={props.index} style={{padding: '5px'}} ref={measuredRef}>{props.text}</div>
    </React.Fragment>
  )
}

class IngredientsSection extends React.Component {

    constructor(props) {
      super(props);
      console.log('in constructor with props:', props);
      this.testref = React.createRef();
      this.state = {
        boundingBox: {right: 0, top: 0},
        boundingBoxes: {},
        boundingBoxesSteps: {}
      };
      console.log('state:', this.state);
      this.updateDimensions = this.updateDimensions.bind(this);
      this.updateStepDimensions = this.updateStepDimensions.bind(this);
    }

    updateDimensions(bbox, index) {
      console.log('updating index ' + index + ' of boundingBoxes', bbox);
      var bboxes = this.state.boundingBoxes;
      bboxes[index] = bbox;
      this.setState({boundingBoxes: bboxes});
    }

    updateStepDimensions(bbox, index) {
      console.log('updating index ' + index + ' of boundingBoxesSteps', bbox);
      var bboxes = this.state.boundingBoxesSteps;
      bboxes[index] = bbox;
      this.setState({boundingBoxesSteps: bboxes});
    }

    render() {
      console.log('rendering ingredientssection...');
      console.log(this.props);
      console.log(this.state);

      const ingredients = this.props.ingredients.map((ingredient, index) => {
        console.log(ingredient, index);
        return (
          <Ingredient
            updateFunc={this.updateDimensions} 
            text={ingredient.ingredients[0]}
            index={index}
            windowSize={this.props.windowSize} />

        );
      });

      const steps = this.props.steps.map((step, index) => {
        console.log(step, index);
        return (
          <Ingredient
            updateFunc={this.updateStepDimensions} 
            text={step}
            index={index}
            windowSize={this.props.windowSize} />
        );
      });

      const ingredient_nodes = Object.keys(this.state.boundingBoxes).map(index => {
        const y_coord = (
          (this.state.boundingBoxes[index].top - this.state.boundingBoxes[0].top) + 
          (this.state.boundingBoxes[index].height / 2));
        return (
          <circle
            fill="white" 
            stroke="black" 
            r="6"
            transform={"translate(10," + y_coord + ")"} />
        );
      })

      const step_nodes = Object.keys(this.state.boundingBoxesSteps).map(index => {
        const y_coord = (
          (this.state.boundingBoxesSteps[index].top - this.state.boundingBoxes[0].top) + 
          (this.state.boundingBoxesSteps[index].height / 2));
        const x_coord = index * 30 + 18;
        return (
          <circle
            fill="white" 
            stroke="black" 
            r="6"
            transform={"translate(" + x_coord + "," + y_coord + ")"} />
        );
      })
      return (
        <div className="bottom">
          <div className="recipe">
            {ingredients}
            {steps}
          </div>
          <svg className="graph">
            {ingredient_nodes}
            {step_nodes}
          </svg>
        </div>
      );
  }
}


class Step extends React.Component {

    getTextWidth(text, font) {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');

      context.font = font || getComputedStyle(document.body).font;

      console.log(context.font);

      return context.measureText(text).width;
    }


    render() {
      return (
        <React.Fragment>
          <foreignObject
            height="20px"
            width="500px"
            transform={"translate(0," + this.props.position[1] + ")"}>
              <div key={this.props.key}>{this.props.text}</div>
          </foreignObject>
        </React.Fragment>
      );
    }
}


class StepsSection extends React.Component {

    render() {
        const steps = this.props.steps.map((step, index) => 
            <Step 
              key={index} 
              text={step.instruction}
              position={[0, index * 20]} />
        );
        return (
            <React.Fragment>
              <g transform={"translate(" + this.props.position[0] + "," + this.props.position[1] + ")"}>
                 {steps}
              </g>
            </React.Fragment>
        );
    }
}

class Recipe extends React.Component {

    constructor(props) {
      super(props);
      this.state = {
        width: window.innerWidth,
        height: window.innerHeight,
        coord: 0
      };
      this.updateDimensions = this.updateDimensions.bind(this);
    }

    componentDidMount() {
      window.addEventListener('resize', this.updateDimensions);
    }

    updateDimensions() {
      console.log('updating dimensions:', window.innerWidth, window.innerHeight);
      this.setState({width: window.innerWidth, height: window.innerHeight});
    }

    render() {
        console.log('rerendering...');
        return (
            <React.Fragment>
                <IngredientsSection 
                      position={[0, 0]}
                      height={this.props.ingredients.length * 20}
                      ingredients={this.props.ingredients}
                      steps={this.props.steps}
                      windowSize={[this.state.width, this.state.height]} />
            </React.Fragment>
        )
    }
}




class Edge extends React.Component {

  render() {
    const bezier = Bezier({points: [this.props.start, this.props.end]})
    return <path d={ bezier.path.print() } fill="none" stroke="gray" />
  }
}



export default Recipe;
