import './index.css';
import React, { useState, useCallback } from 'react';


var Bezier = require('paths-js/bezier');
var Connector = require('paths-js/connector');




// window size controls text position
// ingredient and step text position controls position of nodes
// node position controls position of edges


function MeasuredDiv(props) {

  const measuredRef = useCallback(node => {  
    console.log('in callback for ', node);  
    if (node !== null) {
      console.log('calling update func:', node.getBoundingClientRect(), props.index)
      props.updateFunc(node.getBoundingClientRect(), props.index);
    }  
  }, [props.windowSize]);

  console.log('rendering ingredient:', props);
  return (
    <div key={props.index} className="recipe-item" ref={measuredRef}>{props.text}</div>
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

      // const ingredients = this.props.ingredients.map(ingredient => {
      //   console.log(ingredient);
      //   return (
      //     <MeasuredDiv
      //       updateFunc={this.updateBBox} 
      //       text={ingredient.magnitude + ' ' + ingredient.unit + ' ' + ingredient.name}
      //       index={ingredient.name}
      //       windowSize={this.props.windowSize} />

      //   );
      // });

      let ingredients = [];
      let steps = [];
      for (const node of this.props.graph) {
        if (node.step) {  // a step node
          steps.push(
            <MeasuredDiv
              updateFunc={this.updateBBox} 
              text={node.step.full_text}
              index={node.name}
              windowSize={this.props.windowSize} />
          );
        } else {  // an ingredient node
          const ingredient = this.props.ingredients[node.ingredients[0]];
          ingredients.push(
            <MeasuredDiv
              updateFunc={this.updateBBox} 
              text={ingredient.magnitude + ' ' + ingredient.unit + ' ' + ingredient.name}
              index={node.name}
              windowSize={this.props.windowSize} />
          );
        }
      }


      let coordsMap = {};
      console.log('bboxMap:', this.state.bboxMap);

      const nIngredients = this.props.ingredients.length;
      const nSteps = this.props.graph.length - nIngredients;

      let horizontal_spacing = 10;
      if (this.state.svgBBox) {
        horizontal_spacing = this.state.svgBBox.width / (nSteps + 1);
      }

      this.props.graph.map(node => {
        const key = node.name;
        if (!this.state.bboxMap[key]) {
          return;
        }
        let x_coord, y_coord;

        if (node.step) {  // a step node
          x_coord = (key - this.props.ingredients.length + 1) * horizontal_spacing;
          y_coord = (this.state.bboxMap[key].top - this.state.bboxMap[0].top + 
            (this.state.bboxMap[key].height / 2));
        } else {  // an ingredient node
          x_coord = 10;
          y_coord = (this.state.bboxMap[key].top - this.state.bboxMap[0].top + 
            (this.state.bboxMap[key].height / 2));
        }
        coordsMap[key] = [x_coord, y_coord];
      })

          
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

      const edges = this.props.graph.reduce((acc, node) => {
        const endCoord = coordsMap[node.name];
        if (endCoord) {
          const incomingEdges = node.parents.map(parent => {
            const startCoord = coordsMap[parent];
            console.log(parent, startCoord);
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
                      graph={this.props.graph || []}
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
