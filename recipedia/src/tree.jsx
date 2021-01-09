import './index.css';
import React, { useState, useCallback } from 'react';


var Bezier = require('paths-js/bezier');
var Connector = require('paths-js/connector');




// window size controls text position
// ingredient and step text position controls position of nodes
// node position controls position of edges


function Ingredient(props) {

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
    <div key={props.index} className="recipe-item" ref={measuredRef}>{props.text}</div>
    </React.Fragment>
  )
}

function MeasuredSVG(props) {

  const measuredRef = useCallback(node => {  
    console.log('in callback for ', node);  
    if (node !== null) {
      console.log('calling update func:', node.getBoundingClientRect(), props.index)
      props.updateFunc(node.getBoundingClientRect(), props.index);
    }  
  }, [props.windowSize]);

  console.log('rendering ingredient:', props);
  return (
    <svg 
      ref={measuredRef} 
      className="graph">
        {props.edges}
        {props.nodes}
    </svg>
  )
}

class IngredientsSection extends React.Component {

    constructor(props) {
      super(props);
      console.log('in constructor with props:', props);
      this.testref = React.createRef();
      this.state = {
        bboxMap: {},
        svgBBox: null
      };
      console.log('state:', this.state);

      this.updateBBox = this.updateBBox.bind(this);
      this.updateSVGBBox = this.updateSVGBBox.bind(this);
    }

    updateBBox(bbox, index) {
      console.log('updating index ' + index + ' of nodemap with bbox ', bbox);
      var bboxMap = this.state.bboxMap;
      bboxMap[index] = bbox;
      this.setState({bboxMap: bboxMap});
    }

    updateSVGBBox(bbox) {
      console.log('updating svgBBox to ', bbox);
      this.setState({svgBBox: bbox});
    }

    render() {
      console.log('rendering ingredientssection...');
      console.log(this.props);
      console.log(this.state);

      const ingredients = this.props.ingredients.map(ingredient => {
        console.log(ingredient);
        return (
          <Ingredient
            updateFunc={this.updateBBox} 
            text={ingredient.magnitude + ' ' + ingredient.unit + ' ' + ingredient.ingredients[0]}
            index={ingredient.name}
            windowSize={this.props.windowSize} />

        );
      });

      const steps = this.props.steps.map(step => {
        console.log(step);
        return (
          <Ingredient
            updateFunc={this.updateBBox} 
            text={step.instruction}
            index={step.name}
            windowSize={this.props.windowSize} />
        );
      });

      let coordsMap = {};
      console.log('bboxMap:', this.state.bboxMap);
      const ingredient_node_coords = this.props.ingredients.map(ingredient => {
        console.log('mapping over ingredients');
        const key = ingredient.name;
        if (this.state.bboxMap[key]) {
          const x_coord = 10;
          const y_coord = (this.state.bboxMap[key].top - this.state.bboxMap[0].top + 
            (this.state.bboxMap[key].height / 2));
          coordsMap[key] = [x_coord, y_coord];
        }
      });

      let horizontal_spacing = 10;
      if (this.state.svgBBox) {
        horizontal_spacing = this.state.svgBBox.width / (this.props.steps.length + 1);
      }


      const step_node_coords = this.props.steps.map(step => {
        const key = step.name;
        if (this.state.bboxMap[key]) {
          const x_coord = (key - this.props.ingredients.length + 1) * horizontal_spacing;
          const y_coord = (this.state.bboxMap[key].top - this.state.bboxMap[0].top + 
            (this.state.bboxMap[key].height / 2));

          coordsMap[key] = [x_coord, y_coord];
        }
      });
          
      console.log('coordsMap:', coordsMap);

      const nodes = Object.keys(coordsMap).map(key => {
        return (
            <circle
              fill="white" 
              stroke="black" 
              r="6"
              cx={coordsMap[key][0]}
              cy={coordsMap[key][1]} />
          );
      });

      const edges = this.props.steps.reduce((acc, step) => {
        const endCoord = coordsMap[step.name];
        if (endCoord) {
          const incomingEdges = step.parents.map(parent => {
            const startCoord = coordsMap[parent];

            const connector = Connector({
              start: startCoord,
              end: endCoord,
              tension: 0.1
            });

            return (
              <path d={ connector.path.print() } fill="none" stroke="gray" />
            );
          });
          return acc.concat(incomingEdges);
        }
        
      }, []);

      console.log('edges:', edges);

      return (
        <div className="bottom">
          <div className="recipe">
            {ingredients}
            <div className="divider" />
            {steps}
          </div>
          <MeasuredSVG
            updateFunc={this.updateSVGBBox} 
            windowSize={this.props.windowSize}
            nodes={nodes}
            edges={edges} />
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
                      nodeMap={this.props.nodeMap}
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
