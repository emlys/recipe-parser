import './index.css';
import React, { useState, useCallback } from 'react';


var Bezier = require('paths-js/bezier');
var Connector = require('paths-js/connector');



class LabeledSpan extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      isHovered: false
    }
    this.onMouseEnter = this.onMouseEnter.bind(this);
    this.onMouseLeave = this.onMouseLeave.bind(this);
  }

  onMouseEnter() {
    this.setState(
      {isHovered: true}, 
      () => this.props.mouseEnterCallback(this.props.target));  // after state is set, call the callback
  }

  onMouseLeave() {
    this.setState(
      {isHovered: false},
      () => this.props.mouseLeaveCallback(this.props.target));
  }

  render() {
    const {
      text,  // string
      target,
      onMouseEnter,
      onMouseLeave
    } = this.props;
    console.log('isHovered:', this.state.isHovered);
    return (
      <span 
        style={{fontWeight: 'bold', textDecoration: (this.state.isHovered ? 'underline' : '')}}
        onMouseEnter={this.onMouseEnter}
        onMouseLeave={this.onMouseLeave}>
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
      mouseEnterCallback,  // function
      mouseLeaveCallback   // function
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
            mouseEnterCallback={mouseEnterCallback}
            mouseLeaveCallback={mouseLeaveCallback} />
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
  const {
    index,
    isBold,
    content,
    updateFunc,
    updateDeps,
    className
  } = props;
  console.log('rendering measureddiv ' + index);
  console.log('css class:', className);
  const measuredRef = useCallback(node => {  
    if (node !== null) {
      updateFunc(node.getBoundingClientRect(), index);
    }  
  }, updateDeps);

  return (
    <div 
      key={index} 
      className={className}
      ref={measuredRef}>
        {content}
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
        {props.svgContent}
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
        }, {}),
        isHovered: Object.keys(props.graph).reduce((acc, key) => {
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
      console.log('mouse enter');
      const isBold = this.state.isBold;
      isBold[key] = true;

      const isHovered = this.state.isHovered;
      isHovered[key] = true;
      this.setState({isBold: isBold, isHovered: isHovered});
    }

    onLabelMouseLeave(key) {
      console.log('mouse leave');
      const isBold = this.state.isBold;
      isBold[key] = false;
      
      const isHovered = this.state.isHovered;
      isHovered[key] = false;
      this.setState({isBold: isBold, isHovered: isHovered});
    }

    render() {
      console.log('rendering ingredientssection...');
      console.log(this.props);
      console.log(this.state);

      const ingredients = this.props.ingredients.map((ingredient, index) => {
        return (
          <MeasuredDiv
            updateFunc={this.updateBBox} 
            updateDeps={[this.props.windowSize]}
            content={ingredient.magnitude + ' ' + ingredient.unit + ' ' + ingredient.name}
            index={index}
            className={"recipe-item" + (this.state.isBold[index] ? " hovered-label" : "")}/>
        );
      });

      const steps = this.props.graph.map(node => {
        const step = (
          <Step
            tokens={node.step.tokens}
            verb={node.step.verb}
            labels={node.step.labels}
            fullText={node.step.full_text}
            mouseEnterCallback={this.onLabelMouseEnter}
            mouseLeaveCallback={this.onLabelMouseLeave} />
        );
        return (
          <MeasuredDiv
            updateFunc={this.updateBBox} 
            updateDeps={[this.props.windowSize]}
            content={step}
            index={node.name}
            className={"recipe-item" + (this.state.isHovered[node.name] ? " hovered-label" : "")}/>
        );
      });
 

      let coordsMap = {};

      let horizontal_spacing = 10;
      if (this.state.svgBBox) {
        horizontal_spacing = this.state.svgBBox.width / (this.props.graph.length + 1);
      }

      let x_coord, y_coord;
      this.props.ingredients.map((ingredient, key) => {
        if (!this.state.bboxMap[key]) {
          return;
        }
        x_coord = 10;
        y_coord = (this.state.bboxMap[key].top - this.state.bboxMap[0].top + 
          (this.state.bboxMap[key].height / 2));

        coordsMap[key] = [x_coord, y_coord];
      });

      this.props.graph.map(node => {
        const key = node.name;
        if (!this.state.bboxMap[key]) {
          return;
        }
        x_coord = (key - this.props.ingredients.length + 1) * horizontal_spacing;
        y_coord = (this.state.bboxMap[key].top - this.state.bboxMap[0].top + 
          (this.state.bboxMap[key].height / 2));
      
        coordsMap[key] = [x_coord, y_coord];
      });


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

      // for each node, make a connector from it to each of its parents
      // accumulate all the connectors into a list
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
              <path 
                d={ connector.path.print() } 
                fill="none" 
                stroke="gray" />
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
            svgContent={<g>{edges}{nodes}</g>} />
        </div>
      );
  }
}


export default Recipe;
