var root0 = {label: 'root0',
             children: [{label: 'b0c',
                         children: [{label: 'B'},
                                    {label: '0'},
                                    {label: 'C'}]},
                        {label: 'A'},
                        {label: 'bc1',
                         children: [{label: 'B'},
                                    {label: 'C'},
                                    {label: '1'}]}]};

var root1 = {children: [{label: 'A'},
                        {children: [{label: 'B'},
                                    {label: '0'},
                                    {label: 'C'}]},
                        {children: [{label: 'B'},
                                    {label: 'C'},
                                    {label: '1'}]}]};

var root = root0;

var width  = 720;
var height = 720;

var svg = d3.select('.network')
   .attr('width', width)
   .attr('height', height)
   .append('g').attr('transform', 'translate(0,40)');

var vertex = layOut(root, [720, 720-40]);
var nodes = treeNodes(vertex);
var links = treeLinks(vertex);

svg.selectAll('path')
    .data(links)
  .enter().append('line')
    .attr('x1', function(d) { return d[0].pos[0]; })
    .attr('y1', function(d) { return d[0].pos[1]; })
    .attr('x2', function(d) { return d[1].pos[0]; })
    .attr('y2', function(d) { return d[1].pos[1]; })

var circles = svg.selectAll('circle').data(nodes).enter();
circles.append('circle')
    .attr('cx', function(d) { return d.pos[0]; })
    .attr('cy', function(d) { return d.pos[1]; })
    .attr('r', 10);
circles.append('text')
    .attr('x', function(d) { return d.pos[0] - 5; })
    .attr('y', function(d) { return d.pos[1] + 25; })
    .text(function(d) { return d.node.label; });

