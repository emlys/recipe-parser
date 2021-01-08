import './index.css';
import React, { useState, useCallback } from 'react';


var Bezier = require('paths-js/bezier');




// window size controls text position
// ingredient and step text position controls position of nodes
// node position controls position of edges


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
            text={step.instruction}
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
