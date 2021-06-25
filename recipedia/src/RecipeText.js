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
      highlightColor,
      onMouseEnter,
      onMouseLeave
    } = this.props;

    console.log('text:', text)
    return (
      <span
        style={{
          fontWeight: (isBold ? 'bold' : ''),
          textDecoration: (isUnderlined ? 'underline' : ''),
          fontStyle: (isItalic ? 'italic' : ''),
          backgroundColor: highlightColor,
          whiteSpace: 'pre'}}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}>
          {text}
      </span>
    );
  }
}

class RecipeText extends React.Component {
  constructor(props) {
    super(props);

    const isHovered = {};

    for (const key in props.tokens) {
      isHovered[key] = false;
    }

    this.state = {
      isHovered: isHovered
    }
  }

  render() {
    const {
      tokens,
      isBold,
      isUnderlined,
      isItalic,
      highlightColor,
      onMouseEnterWord,
      onMouseLeaveWord
    } = this.props;

    const punctuation = ['.', ',', '?', '!', ':', ';'];

    let words = [];
    for (let id = 0; id < tokens.length; id++) {
      let text = tokens[id];

      // if the token isn't punctuation, add a space before it
      if (!punctuation.includes(text)) {
        const spaceID = parseInt(id) - 0.5;
        const space = (
          <Span
            id={spaceID}
            text={' '}
            isBold={isBold[spaceID]}
            isUnderlined={isUnderlined[spaceID]}
            isItalic={isItalic[id]}
            // highlightColor={highlightColor[spaceID]}
            onMouseEnter={() => onMouseEnterWord(spaceID)}
            onMouseLeave={() => onMouseLeaveWord(spaceID)}
          />
        );
        words.push(space);
      }

      // add the token
      const word = (
        <Span
          id={parseInt(id)}
          text={text}
          isBold={isBold[id]}
          isUnderlined={isUnderlined[id]}
          isItalic={isItalic[id]}
          highlightColor={highlightColor[id]}
          onMouseEnter={() => onMouseEnterWord(id)}
          onMouseLeave={() => onMouseLeaveWord(id)}
        />
      );
      words.push(word);
    }

    return (
      <div className="recipe-text">
        {words}
      </div>
    );
  }
}

export default RecipeText;
