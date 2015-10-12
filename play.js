var root0 = {id: 1,
             children: [{id: 2,
                         children: [{id: 3, label: 'B'},
                                    {id: 4, label: '0'},
                                    {id: 5, label: 'C'}]},
                        {id: 6, label: 'A'},
                        {id: 10,
                         children: [{id: 7, label: 'B'},
                                    {id: 8, label: 'C'},
                                    {id: 9, label: '1'}]},
                       ]};

var root1 = {id: 1,
             children: [{id: 6, label: 'A'},
                        {id: 2,
                         children: [{id: 3, label: 'B'},
                                    {id: 4, label: '0'},
                                    {id: 5, label: 'C'}]},
                        {id: 10,
                         children: [{id: 7, label: 'B'},
                                    {id: 8, label: 'C'},
                                    {id: 9, label: '1'}]}]};

var roots = [root0, root1];
var which_root = 0;

var width  = 720;
var height = 720;

var svg = d3.select('.network')
    .attr('width', width)
    .attr('height', height)
    .append('g').attr('transform', 'translate(0,40)');

function update() {
    var vertex = layOut(roots[which_root], [720, 720-40]);
    var nodes = treeNodes(vertex);
    var links = treeLinks(vertex);

    var edges =
        svg.selectAll('line')
           .data(links, function(d) { return '' + d[0].node.id + ',' + d[1].node.id; });
    edges.exit().remove();
    edges.enter().append('line');
    edges.transition()
        .attr('x1', function(d) { return d[0].pos[0]; })
        .attr('y1', function(d) { return d[0].pos[1]; })
        .attr('x2', function(d) { return d[1].pos[0]; })
        .attr('y2', function(d) { return d[1].pos[1]; })

    var vertices = 
        svg.selectAll('g')
            .data(nodes, function(d) { assert(d.node.id !== undefined); return d.node.id; });
    vertices.exit().remove();
    vertices.enter().append('g')
        .each(function(d) {
            d3.select(this).append('circle').attr('r', 5);
            d3.select(this).append('text').text(d.node.label);
        });
    vertices = vertices.transition();
    vertices.select('circle')
        .attr('cx', function(d) { return d.pos[0]; })
        .attr('cy', function(d) { return d.pos[1]; });
    //    .attr('fill', 'black')
    vertices.select('text')
        .attr('x', function(d) { return d.pos[0] - 5; })
        .attr('y', function(d) { return d.pos[1] + 25; });
}

update();
d3.select('#toggle').on('click', function() {
    which_root = 1 - which_root;
    update();
});
