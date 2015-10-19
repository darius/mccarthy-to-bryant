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
           .data(links, function(d) { return '' + d.source.node.id + ',' + d.target.node.id; });
    //edges.exit().each(function(d) { console.log('edge exit', d); });
    console.log('exit', edges.exit());
    edges.exit().remove();
    console.log('enter', edges.enter());
    //edges.enter().each(function(d) { console.log('edge enter', d); });
    edges.enter().append('line')
        .attr('x1', function(d) { return d.source.pos[0]; })
        .attr('y1', function(d) { return d.source.pos[1]; })
        .attr('x2', function(d) { return d.target.pos[0]; })
        .attr('y2', function(d) { return d.target.pos[1]; });
    edges.transition()
        .attr('x1', function(d) { return d.source.pos[0]; })
        .attr('y1', function(d) { return d.source.pos[1]; })
        .attr('x2', function(d) { return d.target.pos[0]; })
        .attr('y2', function(d) { return d.target.pos[1]; })

    var vertices = 
        svg.selectAll('g')
            .data(nodes, function(d) { assert(d.node.id !== undefined); return d.node.id; });
    vertices.exit().remove();
    vertices.enter().append('g')
        .each(function(d) {
            d3.select(this).append('circle')
                .attr('r', 5)
                .attr('cx', function(d) { return d.pos[0]; })
                .attr('cy', function(d) { return d.pos[1]; });
            d3.select(this).append('text')
                .attr('x', function(d) { return d.pos[0] - 5; })
                .attr('y', function(d) { return d.pos[1] + 25; })
                .text(function(d) { return d.node.label; });
        });
    vertices = vertices.transition();
    vertices.select('circle')
        .attr('cx', function(d) { return d.pos[0]; })
        .attr('cy', function(d) { return d.pos[1]; });
    //    .attr('fill', 'black')
    vertices.select('text')
        .attr('x', function(d) { return d.pos[0] - 5; })
        .attr('y', function(d) { return d.pos[1] + 25; })
        .text(function(d) { return d.node.label; });
}

update();
d3.select('#toggle').on('click', function() {
    which_root = 1 - which_root;
    update();
});

function transit(lhs, rhs) {
    roots[0] = lhs;
    roots[1] = rhs;
    update();
}

switch (7) {
           case 0: transit({id: 1, label: "a"},
                           {id: 4, children: [{id: 1, label: "a"}, {id: 2, label: "0"}, {id: 3, label: "1"}]});
    break; case 1: transit({id: 1, label: "a"},
                           {id: 2, children: [{id: 3, label: "b"}, {id: 1, label: "a"}, {id: 4, label: "a"}]});
    break; case 2: transit({id: 1, label: "a"},
                           {id: 2, children: [{id: 3, label: "0"}, {id: 1, label: "a"}, {id: 4, label: "b"}]});
    break; case 3: transit({id: 1, label: "b"},
                           {id: 2, children: [{id: 3, label: "1"}, {id: 4, label: "a"}, {id: 1, label: "b"}]});
    break; case 4: transit({id: 1, children: [{id: 2, label: "p"}, {id: 3, label: "a"}, {id: 4, label: "c"}]},
                           {id: 1, children: [{id: 2, label: "p"}, {id: 3, label: "a"}, {id: 5, children: [{id: 6, label: "p"}, {id: 7, label: "b"}, {id: 4, label: "c"}]}]});
    break; case 5: transit({id: 1, children: [{id: 2, label: "p"}, {id: 3, label: "a"}, {id: 4, label: "c"}]},
                           {id: 1, children: [{id: 2, label: "p"}, {id: 5, children: [{id: 7, label: "p"}, {id: 3, label: "a"}, {id: 6, label: "b"}]}, {id: 4, label: "c"}]});
    break; case 6: transit({id: 1, children: [{id: 2, children: [{id: 3, label: "q"}, {id: 4, label: "p"}, {id: 5, label: "r"}]}, {id: 6, label: "a"}, {id: 7, label: "b"}]},
                           {id: 1, children: [{id: 3, label: "q"}, {id: 8, children: [{id: 4, label: "p"}, {id: 6, label: "a"}, {id: 7, label: "b"}]}, {id: 9, children: [{id: 5, label: "r"}, {id: 10, label: "a"}, {id: 11, label: "b"}]}]});

    break; case 7: transit({id: 1, children: [{id: 2, label: "q"}, {id: 3, children: [{id: 4, label: "p"}, {id: 5, label: "a"}, {id: 6, label: "b"}]}, {id: 7, children: [{id: 8, label: "p"}, {id: 9, label: "c"}, {id: 10, label: "d"}]}]},
                           {id: 1, children: [{id: 4, label: "p"}, {id: 3, children: [{id: 2, label: "q"}, {id: 5, label: "a"}, {id: 9, label: "c"}]}, {id: 7, children: [{id: 8, label: "q"}, {id: 6, label: "b"}, {id: 10, label: "d"}]}]});
}
