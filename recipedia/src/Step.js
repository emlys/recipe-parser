import './index.css';
import React from 'react';

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

export default Step;
