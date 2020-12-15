var Bezier = require('paths-js/bezier');
var React = require('react');
var ducks = require('./ducks.json');


function children(x) {
  return x.parents || []
}



function averageXCoords(array) {
    console.log(array)
    var sum = array.reduce(function(a, b){
        return a + b.point[0];
    }, 0);
    // const sum = array.reduce((accumulator, current) => {accumulator + current}, 0);
    return sum / array.length;
}

function numberOfIngredients(nodes) {
    console.log(nodes);
    return nodes.reduce((acc, node) => {
        console.log(node.parents.length);
        if (node.parents.length === 0) {
            return acc + 1;
        } else {
            return acc
        }
    }, 0);
}

function mapNamesToNodes(nodes) {
    // mapping from each node name to the node with that name
    let nodeMap = nodes.reduce((map, node) => {
        map.set(node.name, node);
        return map;
    }, new Map());
    return nodeMap;
}

/**
 * Calculate pixel coordinates for each node in the tree.
 * @param nodes: an array of Nodes
 * @param height: the height in pixels of the whole SVG area
 * @param width: the width in pixels of the whole SVG area
*/
function setNodeCoords(nodes, height, width) {

  let nodeMap = mapNamesToNodes(nodes);
  // the number of rows in the final tree graph
  // all ingredients go in the first row
  // after that, one row per step
  let xCoord, yCoord;

  const nIngredients = numberOfIngredients(nodes);
  const nRows = nodes.length - nIngredients + 1;

  // calculate the horizontal and vertical spacing between nodes
  const xGap = (width - 20) / nIngredients;
  const yGap = (height - 20) / nRows;
  console.log('gaps:', xGap, yGap, height, width, nIngredients, nRows, )

  let ingredientNodes = nodes.slice(0, nIngredients).map(
      (node, index) => {
          xCoord = (index * xGap) + 10 ;
          console.log(index, xGap, xCoord);
          yCoord = 10;
          node.point = [xCoord, yCoord];
          nodeMap.set(node.name, node);
          return node;
      }
  );
  let stepNodes = nodes.slice(nIngredients, nodes.length).map(
      (node, index) => {
          // evenly space the node horizontally between its parent nodes
          xCoord = averageXCoords(node.parents.map(parent => nodeMap.get(parent)));
          console.log(index, nIngredients, yGap);
          yCoord = (index + 1) * yGap + 10;
          node.point = [xCoord, yCoord];
          nodeMap.set(node.name, node);
          return node;
      }
  );
  return ingredientNodes.concat(stepNodes);
}


// Node type:
// {
//  name: string,
//  instruction: string,
//  ingredients: list[string],
//  parents: list[int]
//}

class RecipeTree extends React.Component {


  constructor(props) {
    super(props);
    this.buildEdges = this.buildEdges.bind(this);
  }

  /**
   * Given a list of nodes, make a Bezier curve representing each edge
   */
  buildEdges(nodes) {
    var beziers = nodes.reduce((acc, node) => {
        // make a connector edge between the node and each of its parents
        const incomingEdges = node.parents.map((parent) => {
            console.log([nodes[parent].point, node.point]);
            var bezier = Bezier({
                points: [nodes[parent].point, node.point]
            });
            return bezier;
        });
        return acc.concat(incomingEdges);
    }, []);
    return beziers;
  }

  render() {

    let {nodes,} = this.props;

    setNodeCoords(nodes, 380, 500);

    const edges = this.buildEdges(nodes);

    var paths = edges.map(function(c) {
      return <path d={ c.path.print() } fill="none" stroke="gray" />
    })

    var circles = nodes.map(function(n) {
      console.log('plotting at', n.point);
      var position = "translate(" + n.point[0] +"," + n.point[1]  +")";


      return (
        <g transform={ position }>
          <circle fill="white" stroke="black" r="5" cx="0" cy="0"/>
        </g>
      )
    })

    return (
      <div id="tree">
        <svg width="500" height="380">
          <g>
            { paths }
            { circles }
          </g>
        </svg>
      </div>
    )
  }
}

export default RecipeTree;
