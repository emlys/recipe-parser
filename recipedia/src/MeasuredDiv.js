import './index.css';
import React, { useCallback } from 'react';

/* A self-measuring div that reports its measurements
 *
 * index: identifying value to pass to callback
 * content: any JSX content to render within the measured div
 * updateFunc: measurement reporting function that takes (bbox, index)
 * updateDeps: array of things to check when determining whether to report
    (typically windowSize)
 * className: name of CSS class to apply to the div
 */
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

export default MeasuredDiv;
