function assert(ok, plaint) {
    if (!ok) throw new Error("Assertion failed: " + plaint);
}

function treeNodes(tree) {
    var nodes = [];
    function walk(node) {
        nodes.push(node);
        var i, n = node.children.length;
        for (i = 0; i < n; ++i) {
            walk(node.children[i]);
        }
    }
    walk(tree);
    return nodes;
}

function treeLinks(tree) {
    var links = [];
    function walk(node) {
        var i, n = node.children.length;
        for (i = 0; i < n; ++i) {
            links.push({source: node, target: node.children[i]});
            walk(node.children[i]);
        }
    }
    walk(tree);
    return links;
}

// Given a binary tree of nodes like {children}, return a tree of
// vertices like {node, pos, children}, where node points back to the
// corresponding node of the input binary tree. (A vertex also has
// profile and offset fields, used internally.)
// :bounds is [width, height] of the available area.
function layOut(tree, bounds) {
    var root = copy(tree);
//    var D = depth(tree);
    fit(root); root.offset = 0;
    rescale(root, [bounds[0]/2, 0], bounds);
    return root;
}

// Return the count of levels in :tree.
function depth(tree) {
    var i, n = tree.children.length;
    var deepest = 0;
    for (i = 0; i < n; ++i) {
        deepest = Math.max(deepest, depth(tree.children[i]));
    }
    return deepest + 1;
}

// Return a tree like :tree but with only {node, children} fields, with
// node pointing back to the corresponding node of the input tree.
function copy(tree) {
    var vertex = {node: tree, children: []};
    var i, n = tree.children !== undefined ? tree.children.length : 0;
    for (i = 0; i < n; ++i) {
        vertex.children.push(copy(tree.children[i]));
    }
    return vertex;
}

// Compute the profile of :tree as it will be laid out. This is a
// list of [x_lo, x_hi] pairs, one for each level. (With the x's as yet
// unscaled to the available area.) Also set vertex.offset fields.
function fit(tree) {
    if (tree.children.length === 0) {
        tree.profile = [[0, 0]];
    } else {
        assert(tree.children.length === 3, "Ternary trees only");

        tree.children.forEach(fit);
        var index = tree.children[0];
        var left  = tree.children[1];
        var right = tree.children[2];

        var space = repel(left.profile, right.profile);
        right.offset = space/2;
        left.offset  = -right.offset;

        var lr = span([[0,0]], delay(span(shift(left),
                                          shift(right))));
        index.offset = -repel(index.profile, lr);

        tree.profile = span(shift(index), lr);
    }    
}

function repel(left_profile, right_profile) {
    var i, n = Math.min(left_profile.length, right_profile.length);
    var w = 0; // Max width so far
    for (i = 0; i < n; ++i) {
        var lp = left_profile[i];
        var rp = right_profile[i];
        if (lp !== undefined && rp !== undefined)
            w = Math.max(w, lp[1] - rp[0]);
    }
    return w + 1;               // add padding
}

function shift(tree) {
    return tree.profile.map(function(interval) {
        return [tree.offset + interval[0], tree.offset + interval[1]];
    });
}

function delay(profile) {
    return [undefined].concat(profile);
}

function span(profile1, profile2) {
    var i, n = Math.max(profile1.length, profile2.length);
    var result = [];
    for (i = 0; i < n; ++i) {
        var p1 = profile1[i];
        var p2 = profile2[i];
        var p = undefined;
        if (p1 === undefined && p2 !== undefined) {
            p = p2.slice();
        } else if (p1 !== undefined && p2 === undefined) {
            p = p1.slice();
        } else if (p1 !== undefined && p2 !== undefined) {
            p = [p1[0], p2[1]];
            assert(p[0] === Math.min(p1[0], p2[0]));
            assert(p[1] === Math.max(p1[1], p2[1]));
        }
        result.push(p);
    }
    return result;
}

var dx = 30;
var dy = 60;

// Fill in the pos fields of :tree, with the root at :pos.
function rescale(tree, pos, bounds) {
    tree.pos = pos;
    if (tree.children.length !== 0) {
        assert(tree.children.length === 3, "Ternary trees only");
        rescale(tree.children[0], [pos[0] + tree.children[0].offset * dx, pos[1]], bounds);
        rescale(tree.children[1], [pos[0] + tree.children[1].offset * dx, pos[1] + dy], bounds);
        rescale(tree.children[2], [pos[0] + tree.children[2].offset * dx, pos[1] + dy], bounds);
    }    
}

function inspect(v) {
    console.log(v.node.label, v.offset, ':', outline(v.profile));
}

function outline(sil) {
    var s = '';
    for (var i = 0; i < sil.length; ++i) {
        s += ' ' + sil[i][0] + ',' + sil[i][1];
    }
    return s;
}
