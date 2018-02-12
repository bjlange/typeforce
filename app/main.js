import * as d3 from "d3";
import Chain from "markov-chains";
import * as _ from "lodash";
require("./main.scss"); // will build CSS from SASS 3 file

// Main
const words =
  "This chapter is an effort to build an ironic political myth faithful to feminism, socialism, and materialism. Perhaps more faithful as blasphemy is faithful, than as reverent worship and identification. Blasphemy has always seemed to require taking things very seriously. I know no better stance to adopt from within the secular-religious, evangelical traditions of United States politics, including the politics of socialist feminism. Blasphemy protects one from the moral majority within, while still insisting on the need for community. Blasphemy is not apostasy. Irony is about contradictions that do not resolve into larger wholes, even dialectically, about the tension of holding incompatible things together because both or all are necessary and true. Irony is about humour and serious play. It is also a rhetorical strategy and a political method, one I would like to see more honoured within socialist-feminism. At the centre of my ironic faith, my blasphemy, is the image of the cyborg.";
const word_arr = words.split(" ");

d3.csv("data-capture-2-7-940.csv", data => {
  // console.log(data);
  let sequences = [];
  let subsequence = [];
  for (let row of data) {
    if (row.xxz == 1 && subsequence.length > 0) {
      sequences.push(subsequence);
      const vizDiv = document.getElementById("viz");
      let svg = d3
        .select(vizDiv)
        .append("svg")
        .attr("width", 300)
        .attr("height", 400);
      draw_comp(subsequence, svg)
      subsequence = [];
    }
    row["word"] = word_arr[row.xxz - 1];
    delete row.xxz;
    const key_renames = {
      "x (out of 300)": "x",
      "y (out of 400)": "y",
      "# of characters": "chars",
      "font size": "size",
      "font weight": "weight"
    };
    row = _.mapKeys(row, function(value, key) {
      return key_renames[key] || key;
    });    
    subsequence.push(row);
  }
  console.log(sequences);
  const chain = new Chain(sequences);
  for (let i of _.range(0, 30)) {
    // const vizDiv = document.getElementById("viz");
    // let svg = d3
    //   .select(vizDiv)
    //   .append("svg")
    //   .attr("width", 300)
    //   .attr("height", 400);
    // let data = chain.walk();
    // draw_comp(data, svg)
  }
});

function draw_comp(data, svg) {
  svg
    .selectAll("text")
    .data(data)
    .enter()
    .append("text")
    .attr("x", d => d.x)
    .attr("y", d => parseInt(d.y))
    .attr("text-anchor", "start")
    .attr("transform-origin", "bottom right")
    .attr("transform", d => "rotate(" + -d.rotation + " " + d.x + " " + d.y + ")")
    .attr("font-size", d => d.size)
    .attr("class", d => d.weight)
    .attr("font-family", "Helvetica Neue")
    .text(d => dadata(d.chars));
}

function dadata(len) {
  return _.repeat('dadata', Math.ceil(len / 6)).slice(0, len)
}