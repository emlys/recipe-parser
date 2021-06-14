import './index.css';
import React from 'react';

const spacer = '   .'.repeat(500);

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
    if (Math.floor(magnitude * 100) === 66 | Math.floor(magnitude * 100) === 67) {
      magnitude = '2/3';
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

export default Ingredient;

