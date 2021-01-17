import './index.css';
import React, { useState, useCallback } from 'react';


var Bezier = require('paths-js/bezier');
var Connector = require('paths-js/connector');



class LabeledSpan extends React.Component {

  render() {
    const {
      text,  // string
      target,
      onMouseEnter,
      onMouseLeave
    } = this.props;

    return (
      <span 
        style={{fontWeight: 'bold'}}
        onMouseEnter={() => onMouseEnter(target)}
        onMouseLeave={() => onMouseLeave(target)}>
          {text}
      </span>
    );
  }
}


class Step extends React.Component {

  render() {
    const {
      tokens,        // object
      verb,          // integer
      labels,        // object
      fullText,      // string
      onMouseEnter,  // function
      onMouseLeave   // function
    } = this.props;

    let formattedTokens = [];
    const punctuation = ['.', ',', '?', '!', ':', ';'];

    const indices = Object.keys(tokens);
    const min = Math.min(...indices);
    const max = Math.max(...indices);
    let key = min;

    let spans = [];  // accumulate spans 
    let span = [];  // accumulate tokens in the current span
    while (key <= max) {
      let token = tokens[key];

      // put a space before each token, unless it's punctuation, or the first word
      if (key > min && !punctuation.includes(token)) {
        token = ' ' + token;
      }

      if (labels[key]) {  // this is the start of a labeled section

        // close the current span and start a new one
        if (span.length > 0) {  // only create a span if it has content
          spans.push(<span>{span}</span>);
          span = [token];
        }

        // add each word from the labeled range into a separate span
        // this way the whole thing can be made bold or underlined
        let i = key + 1;
        while (i <= labels[key].end) {
          let token = tokens[i];
          // put a space before each token, unless it's punctuation, or the first word
          if (i > min && !punctuation.includes(token)) {
            token = ' ' + token;
          }
          span.push(token);
          i += 1;
        }
        // a span that has hovering behavior
        spans.push(
          <LabeledSpan
            text={span}
            target={labels[key].node_index}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave} />
        );
        key = i;
        span = [];
      } else {
        span.push(token);
        key += 1;
      }
    }
    // complete the final span
    spans.push(<span>{span}</span>);
    return (<div>{spans}</div>);
  }
}


// window size controls text position
// ingredient and step text position controls position of nodes
// node position controls position of edges


function MeasuredDiv(props) {

  const measuredRef = useCallback(node => {  
    if (node !== null) {
      props.updateFunc(node.getBoundingClientRect(), props.index);
    }  
  }, [props.windowSize]);

  return (
    <div 
      key={props.index} 
      className="recipe-item"
      style={props.isBold ? {fontWeight: 'bold'} : {}} 
      ref={measuredRef}>
        {props.content}
    </div>
  )
}

function MeasuredSVG(props) {

  const measuredRef = useCallback(node => {  
    if (node !== null) {
      props.updateFunc(node.getBoundingClientRect(), props.index);
    }  
  }, [props.windowSize]);

  return (
    <svg 
      ref={measuredRef} 
      className="graph">
        {props.edges}
        {props.nodes}
    </svg>
  )
}

class Recipe extends React.Component {

    constructor(props) {
      super(props);
      this.testref = React.createRef();
      this.state = {
        bboxMap: {},
        svgBBox: null,
        isBold: Object.keys(props.ingredients).reduce((acc, key) => {
          acc[key] = false;
          return acc;
        }, {})
      };
      console.log('state:', this.state);

      this.updateBBox = this.updateBBox.bind(this);
      this.updateSVGBBox = this.updateSVGBBox.bind(this);
      this.onLabelMouseEnter = this.onLabelMouseEnter.bind(this);
      this.onLabelMouseLeave = this.onLabelMouseLeave.bind(this);
    }

    updateBBox(bbox, index) {
      console.log('updating index ' + index + ' of nodemap with bbox ', bbox);
      const bboxMap = this.state.bboxMap;
      bboxMap[index] = bbox;
      this.setState({bboxMap: bboxMap});
    }

    updateSVGBBox(bbox) {
      console.log('updating svgBBox to ', bbox);
      this.setState({svgBBox: bbox});
    }

    onLabelMouseEnter(key) {
      console.log('setting ' + key + ' to bold');
      const isBold = this.state.isBold;
      isBold[key] = true;
      this.setState({isBold: isBold})
    }

    onLabelMouseLeave(key) {
      const isBold = this.state.isBold;
      isBold[key] = false;
      this.setState({isBold: isBold})
    }

    render() {
      console.log('rendering ingredientssection...');
      console.log(this.props);
      console.log(this.state);

      let ingredients = [];
      let steps = [];
      for (const node of this.props.graph) {
        if (node.step) {  // a step node
          const step = (
            <Step
              tokens={node.step.tokens}
              verb={node.step.verb}
              labels={node.step.labels}
              fullText={node.step.full_text}
              onMouseEnter={this.onLabelMouseEnter}
              onMouseLeave={this.onLabelMouseLeave} />
          );
          steps.push(
            <MeasuredDiv
              updateFunc={this.updateBBox} 
              content={step}
              index={node.name}
              windowSize={this.props.windowSize} />
          );
        } else {  // an ingredient node
          const ingredient = this.props.ingredients[node.ingredients[0]];
          ingredients.push(
            <MeasuredDiv
              updateFunc={this.updateBBox} 
              content={ingredient.magnitude + ' ' + ingredient.unit + ' ' + ingredient.name}
              index={node.name}
              windowSize={this.props.windowSize}
              isBold={this.state.isBold[node.name]} />
          );
        }
      }

      const nIngredients = this.props.ingredients.length;
      const nSteps = this.props.graph.length - nIngredients;

      let coordsMap = {};

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


export default Recipe;
