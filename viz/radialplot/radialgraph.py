
import numpy as np
from random import randint

from bokeh.document import Document
from bokeh.mixins import LineProps, TextProps
from bokeh.objects import (DataSource, ColumnDataSource)
from bokeh.plotting import circle, figure, hold, output_file, show, segment
from bokeh.properties import (Any, HasProps, Include, Instance, List, Int, Float)
from bokeh.session import Session

class RadialGraph(HasProps):
    
    # The start/end angles of the radial plot in degrees
    start_angle = Float
    end_angle = Float

    # The datasources containing ata for the graph
    _node_source = Instance(DataSource)
    _edge_source = Instance(DataSource)

    _session = Any
    _doc = Any

    def __init__(self, **kw):
        super(RadialGraph, self).__init__(**kw)
        self._node_source = ColumnDataSource(dict(id=[], time=[], relevance=[]))
        self._edge_source = ColumnDataSource(dict(parent=[], child=[]))

        self._session = Session()
        self._doc = Document()

    def update_data(self, nodes, edges):
        """ Provides updated data for the datasources.
        
        nodes: list of tuples (id, timestamp, relevance)
        edges: list of tuples (parent id, child id)

        All parent & child IDs need to be in the updated nodes list.
        """

def make_fake_data(num_start_nodes, num_steps, max_span_out):
    """ 
    Returns (ids, times, edgelist)
    """
    nodes = range(num_start_nodes)
    times = [0]*num_start_nodes
    edges = []
    
    last_frontier = nodes[:]   # IDs of the frontier
    frontier = []
    maxid = num_start_nodes-1  # last actual ID
    for generation in range(num_steps):
        for node in last_frontier:
            num_new_nodes = randint(0, max_span_out)
            if num_new_nodes == 0:
                continue
            new_nodes = range(maxid+1, maxid+num_new_nodes+1)
            maxid += num_new_nodes
            new_edges = [(node, x) for x in new_nodes]
            frontier.extend(new_nodes)
            edges.extend(new_edges)
        nodes.extend(frontier)
        times.extend([generation+1]*len(frontier))
        last_frontier = frontier
        frontier = []

    return np.array((nodes, times)).T, np.array(edges)

def _layout_nodes(nodes):
    """ Given the list of nodes (Nx2 of node IDs and times), returns a new
    length-N array which provides some canonical Y position for each node.
    The times are assumed to be contiguous and monotonic.
    """
    # Conceptually, we just need to pivot and compute the max-Y.  But the
    # way we'll actually do this is by taking advantage of the fact that 
    # the times are monotonic.
    # TODO: Fix some of the edge cases (e.g. when there is just one node 
    # in the last time slot); make robust if input times are not monotonic
    times = nodes[:,1]
    yindex = np.hstack(([0], np.where(times[1:] - times[:-1] != 0)[0] + 1, [len(times)]))
    ycounts = yindex[1:] - yindex[:-1]
    yvals = np.empty_like(times)

    for start, count in zip(yindex,ycounts):
        yvals[start:start+count] = np.arange(count)
    return yvals


def crawlchart(nodes, edgelist):
    """ edges is an Nx2 array of node ids 
    """
    # Need to map incrementing list of node IDs to actual Y values
    ids, times = nodes.T
    node_y = _layout_nodes(nodes)
    hold()
    circle(times, node_y, color="red", size=3)

    nodepos = np.asarray((times,node_y)).T
    coords = nodepos[edgelist].reshape((len(edgelist), 4)).T
    segment(coords[0], coords[1], coords[2], coords[3],
            line_alpha=0.35)

    
def main():
    nodes, edges = make_fake_data(50, 80, 2)
    figure(plot_width=1000, plot_height=500)
    output_file("plot.html")
    crawlchart(nodes, edges)
    show()


if __name__ == "__main__":
    main()


