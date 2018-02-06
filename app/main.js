import * as d3 from 'd3';

// Local imports
// import { createCircleChart } from './circle';  // named import
// import makeBarChart from './bar';  // name is irrelevant since it is a default export

require('./main.scss'); // will build CSS from SASS 3 file

// Main
const vizDiv = document.getElementById('viz');

const data = [];

const svg = d3
  .select(vizDiv)
                .append('svg')
  .attr('width', 1000)
  .attr('height', 2000);

let working_x = 500;
let working_y = 15;
const words = 'as pioneers of human-centered design, we keep people at the center of our work. it\'s a key tenet of design thinking, and even as our methods evolve in response to new, complex challenges, we’re always designing solutions for people first. we’re building to learn, and learning as we build, through inspiration, ideation, and implementation.';
for (const word of words.split(' ')) {
  working_x += Math.floor((Math.random() - 0.5) * 50);
  working_y += 20;
  data.push({ x: working_x, y: working_y, word });
}

// Main
const vizDiv = document.getElementById("viz");

svg
  .selectAll('text')
  .data(data)
  .enter()
  .append('text')
  .attr('x', (d) => {
    return d.x;
  })
  .attr('y', (d) => {
    return d.y;
  })
  .text((d) => {
    return d.word;
  });
