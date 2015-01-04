
import numpy as np
from numpy import pi, cos, sin
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
    Returns ((node ids, times, relevance), edgelist) where
    node IDs are unique integers, times are generally increasing
    numbers, and relevance is a random score between 0 and 1
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
    
    # Gaussian distribution of relevance
    relevance = np.fabs(np.random.normal(size=len(times)))
    # Flat (uniform) distribution of relevance
    # relevance = np.random.uniform(size=len(times))

    return np.array((nodes, times, relevance)).T, np.array(edges)

def _rectilinear_layout(nodes):
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
    relevances = nodes[:,2]
    yindex = np.hstack(([0], np.where(times[1:] - times[:-1] != 0)[0] + 1, [len(times)]))
    ycounts = yindex[1:] - yindex[:-1]
    yvals = np.empty_like(times)

    for start, count in zip(yindex,ycounts):
        # Uncomment the following if unsorted is desired
        #yvals[start:start+count] = np.linspace(-count/2.0, count/2.0, count)
        # Sort by relevance
        rel = np.argsort(relevances[start:start+count])
        yvals[rel+start] = np.linspace(-count/2.0, count/2.0, count)
    return yvals


def crawlchart(nodes, edgelist):
    """ edges is an Nx2 array of node ids 
    """
    ids, times, relevances = nodes.T
    times *= 2
    node_y = _rectilinear_layout(nodes)
    hold()
    #circle(times, node_y, color="gray", size=1)

    # Draw the relevant points in a different color
    circle(times, node_y, color="red", size=relevances*6, alpha=relevances)

    nodepos = np.asarray((times,node_y)).T
    coords = nodepos[edgelist].reshape((len(edgelist), 4)).T
    segment(coords[0], coords[1], coords[2], coords[3],
            line_alpha=0.35)

def _radial_layout(nodes):
    """ Returns Xs and Ys """
    times = nodes[:,1]
    relevances = nodes[:,2]
    yindex = np.hstack(([0], np.where(times[1:] - times[:-1] != 0)[0] + 1, [len(times)]))
    ycounts = yindex[1:] - yindex[:-1]
    
    xvals = np.empty_like(times)
    yvals = np.empty_like(times)

    for i, (start, count) in enumerate(zip(yindex, ycounts)):
        r = (i+1)*15
        thetas = np.linspace(0, 2*pi, count)
        xvals[start:start+count] = r * cos(thetas)
        yvals[start:start+count] = r * sin(thetas)
    return xvals, yvals

def radialchart(nodes, edgelist):
    ids, times, relevances = nodes.T
    times *= 2
    node_x, node_y = _radial_layout(nodes)
    nodepos = np.asarray((node_x, node_y)).T
    hold()
    circle(node_x, node_y, color="red", size=relevances*4, alpha=relevances)
    coords = nodepos[edgelist].reshape((len(edgelist), 4)).T
    segment(coords[0], coords[1], coords[2], coords[3],
            line_alpha=0.35)
    
def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "radial":
        nodes, edges = make_fake_data(20, 200, 2)
        figure(plot_width=1000, plot_height=1000, x_axis_type=None, y_axis_type=None)
        output_file("radial.html")
        radialchart(nodes, edges)
        show()
        
    else:
        nodes, edges = make_fake_data(100, 80, 2)
        figure(plot_width=1000, plot_height=400, y_axis_type=None)
        output_file("crawl.html")
        crawlchart(nodes, edges)
        show()


if __name__ == "__main__":
    main()


