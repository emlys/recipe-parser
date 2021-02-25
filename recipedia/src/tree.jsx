import './index.css';
import React, { useState, useCallback } from 'react';

var Connector = require('paths-js/connector');

const spacer = '   .'.repeat(500);


class Span extends React.Component {
  render() {
    const {
      id,
      text,
      isBold,
      isUnderlined,
      isItalic,
      onMouseEnter,
      onMouseLeave
    } = this.props;
    // console.log('isItalic:', isItalic);
    return (
      <span
        style={{
          fontWeight: (isBold ? 'bold' : ''),
          textDecoration: (isUnderlined ? 'underline' : ''),
          fontStyle: (isItalic ? 'italic' : '')}}
        onMouseEnter={() => onMouseEnter(id)}
        onMouseLeave={() => onMouseLeave(id)}>
          {text}
      </span>
    );
  }
}

class Step extends React.Component {
  constructor(props) {
    super(props);

    const wordToTargets = {};
    const isUnderlined = {};
    const isBold = {};
    const isItalic = {};

    for (const key in props.tokens) {
      isBold[key] = false;
      isUnderlined[key] = false;
      isItalic[key] = false;
    }
    // invert the mapping so that, for each word, we can look up its target(s)
    for (const key in props.labels) {
      for (const wordID of props.labels[key]) {
        if (wordToTargets[wordID]) {
          wordToTargets[wordID].push(key);
        } else {
          wordToTargets[wordID] = [key];
        }
        // make labeled words bold so that they look hoverable
        isBold[wordID] = true;
      }
    }
    isItalic[props.verbIndex] = true;

    this.state = {
      // a boolean saying whether each token should be bold
      isBold: isBold,
      isUnderlined: isUnderlined,
      isItalic: isItalic,
      wordToTargets: wordToTargets
    }

    this.onMouseEnterWord = this.onMouseEnterWord.bind(this);
    this.onMouseLeaveWord = this.onMouseLeaveWord.bind(this);
  }

  onMouseEnterWord(key) {
    const isUnderlined = this.state.isUnderlined;

    const targets = this.state.wordToTargets[key];
    if (targets && targets.length) {
      for (const target of targets) {
        for (const word of this.props.labels[target]) {
          isUnderlined[word] = true;
        }
        this.props.onMouseEnterLabel(target);
      }
      this.setState({isUnderlined: isUnderlined})
    }
  }

  onMouseLeaveWord(key) {
    const isUnderlined = this.state.isUnderlined;

    const targets = this.state.wordToTargets[key];
    if (targets && targets.length) {
      for (const target of targets) {
        for (const word of this.props.labels[target]) {
          isUnderlined[word] = false;
        }
        this.props.onMouseLeaveLabel(target);
      }
      this.setState({isUnderlined: isUnderlined});
    }
  }

  render() {
    const { tokens } = this.props;

    const punctuation = ['.', ',', '?', '!', ':', ';'];

    const min = Math.min(...Object.keys(tokens)).toString();
    const max = Math.max(...Object.keys(tokens)).toString();
    let words = [];
    for (let id of Object.keys(tokens)) {
      let text = tokens[id];
      if (id === min) {
        text = text.charAt(0).toUpperCase() + text.slice(1);
      }

      // if the token isn't punctuation, add a space before it
      if (!punctuation.includes(text)) {
        const spaceID = parseInt(id) - 0.5;
        const space = (
          <Span
            id={spaceID}
            text={' '}
            isBold={this.state.isBold[spaceID]}
            isUnderlined={this.state.isUnderlined[spaceID]}
            onMouseEnter={this.onMouseEnterWord}
            onMouseLeave={this.onMouseLeaveWord}
          />
        );
        words.push(space);
      }

      if (id === max && punctuation.includes(text)) {
        continue;  // drop trailing punctuation
      }
      console.log(this.state.isItalic);
      // add the token
      const word = (
        <Span
          id={parseInt(id)}
          text={text}
          isBold={this.state.isBold[id]}
          isUnderlined={this.state.isUnderlined[id]}
          isItalic={this.state.isItalic[id]}
          onMouseEnter={this.onMouseEnterWord}
          onMouseLeave={this.onMouseLeaveWord}
        />
      );
      words.push(word);
    }
    words.push(
      <Span
          id={-1}
          text={'.'}
          isBold={false}
          isUnderlined={false}
          isItalic={false}
          onMouseEnter={() => {}}
          onMouseLeave={() => {}}
        />
    );

    return (
      <React.Fragment>
        {words}
      </React.Fragment>
    );
  }
}


class Ingredient extends React.Component {
  render() {
    let {
      magnitude,
      unit,
      name,
      isBold
    } = this.props;

    if (unit === 'dimensionless') {
      unit = '';
    }
    if (magnitude > 1) {
      unit += 's';
    }
    if (Math.floor(magnitude * 100) === 33) {
      magnitude = '1/3';
    }
    if (magnitude === 0) {
      magnitude = '';
    }

    return (
      <div className='ingredient'>
        <span className='ingredient-magnitude'>
          {magnitude + ' ' + unit}
        </span>
        <span className='spacer'>
          {spacer}
        </span>
        <span 
          className='ingredient-name' 
          style={{
            fontWeight: (isBold ? 'bold' : ''),
            textDecoration: (isBold ? 'underline' : '')
            }} >
          {name}
        </span>
      </div>
    );
  }
}

// window size controls text position
// ingredient and step text position controls position of nodes
// node position controls position of edges


function MeasuredDiv(props) {
  const {
    index,
    content,
    updateFunc,
    updateDeps,
    className
  } = props;
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

    this.updateBBox = this.updateBBox.bind(this);
    this.updateSVGBBox = this.updateSVGBBox.bind(this);
    this.onLabelMouseEnter = this.onLabelMouseEnter.bind(this);
    this.onLabelMouseLeave = this.onLabelMouseLeave.bind(this);
  }

  updateBBox(bbox, index) {
    const bboxMap = this.state.bboxMap;
    bboxMap[index] = bbox;
    this.setState({bboxMap: bboxMap});
  }

  updateSVGBBox(bbox) {
    this.setState({svgBBox: bbox});
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
    console.log('rendering ingredientssection...');
    console.log(this.props);
    console.log(this.state);
    const {
      ingredients,
      steps,
      graph,
      extras,
      windowSize
    } = this.props;

    const {
      bboxMap,
      svgBBox,
      isBold
    } = this.state;

    const ingredientDivs = ingredients.map(index => {
      const ingredient = graph[index];
      
      return (
        <MeasuredDiv
          updateFunc={this.updateBBox} 
          updateDeps={[windowSize]}
          index={index}
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
    });

    console.log('graph:', graph);
    const textOrder = steps.concat(extras).sort((a, b) => a - b);
    console.log('order:', textOrder, typeof(textOrder[0]));


    let groups = []
    if (Object.keys(graph).length) {
      let group = [graph[textOrder[0]]];
      console.log('groups:', groups);
      for (const key of textOrder.slice(1)) {
        const step = graph[key];
        if (step.parents) { // a node
          groups.push(group);
          console.log('groups:', groups);
          group = [step];
        } else {  // extra info
          group.push(step);
        }
      }
      groups.push(group);
      console.log('groups:', groups);
    }

    const stepDivs = groups.map(group => {
      console.log('group:', group);
      const stepSpans = group.map(step => {
        const stepDiv = (
          <Step
            tokens={step.tokens}
            verbIndex={step.verb_index}
            labels={step.labels}
            onMouseEnterLabel={this.onLabelMouseEnter}
            onMouseLeaveLabel={this.onLabelMouseLeave} />
        );
        return (
          <MeasuredDiv
            updateFunc={this.updateBBox} 
            updateDeps={[windowSize]}
            content={stepDiv}
            className="step"
          />
        );
      });
      return (
        <div className='step-group'>
          {stepSpans}
        </div>
      );
    });


    // scale the spacing between nodes to fit the window width
    let horizontalSpacing = 10;
    if (svgBBox) {
      horizontalSpacing = svgBBox.width / (steps.length + 1);
    }

    const coordsMap = {};
    let x_coord, y_coord;
    // set coordinates for each ingredient node
    for (const key of ingredients) {
      if (!bboxMap[key]) {
        continue;
      }
      x_coord = 10;
      y_coord = (bboxMap[key].top - bboxMap[0].top + 
        (bboxMap[key].height / 2));

      coordsMap[key] = [x_coord, y_coord];
    }

    // set coordinates for each step node
    for (const [index, key] of steps.entries()) {
      if (!bboxMap[key]) {
        continue;
      }
      x_coord = (index + 1) * horizontalSpacing;
      y_coord = (bboxMap[key].top - bboxMap[0].top + 
        (bboxMap[key].height / 2));
      
      coordsMap[key] = [x_coord, y_coord];
    }

    // make a svg for each node
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
    let edges = [];
    for (const key of steps) {
      const endCoord = coordsMap[key];
      const node = graph[key];

      if (endCoord) {
        for (const parent of node.parents) {
          const startCoord = coordsMap[parent];
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

    const divider = (ingredientDivs.length ? <div className="divider" /> : <div />);
    return (
      <div className="bottom">
        <div className="recipe">
          {ingredientDivs}
          {divider}
          {stepDivs}
        </div>
        <MeasuredSVG
          updateFunc={this.updateSVGBBox} 
          windowSize={windowSize}
          svgContent={<g>{edges}{nodes}</g>} />
      </div>
    );
  }
}


export default Recipe;
