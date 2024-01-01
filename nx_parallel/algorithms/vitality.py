from functools import partial
import os
from joblib import Parallel, delayed
import networkx as nx

__all__ = ["closeness_vitality"]


def closeness_vitality(G, node=None, weight=None, wiener_index=None, n_jobs=-1):
    """Returns the closeness vitality for nodes in `G`. Parallel implementation.

    The *closeness vitality* of a node, defined in Section 3.6.2 of [1],
    is the change in the sum of distances between all node pairs when
    excluding that node.

    Parameters
    ----------
    G : NetworkX graph
        A strongly-connected graph.

    weight : string
        The name of the edge attribute used as weight. This is passed
        directly to the :func:`~networkx.wiener_index` function.

    node : object
        If specified, only the closeness vitality for this node will be
        returned. Otherwise, a dictionary mapping each node to its
        closeness vitality will be returned.

    n_jobs : int, optional (default=-1)
        The number of logical CPUs or cores you want to use. 
        If `-1` all available cores are used.
        For `n_jobs` less than `-1`, (`n_cpus + 1 + n_jobs`) are used.
        If an invalid value is given, then `n_jobs` is set to `os.cpu_count()`.

    Other parameters
    ----------------
    wiener_index : number
        If you have already computed the Wiener index of the graph
        `G`, you can provide that value here. Otherwise, it will be
        computed for you.

    Returns
    -------
    dictionary or float
        If `node` is None, this function returns a dictionary
        with nodes as keys and closeness vitality as the
        value. Otherwise, it returns only the closeness vitality for the
        specified `node`.

        The closeness vitality of a node may be negative infinity if
        removing that node would disconnect the graph.

    References
    ----------
    .. [1] Ulrik Brandes, Thomas Erlebach (eds.).
           *Network Analysis: Methodological Foundations*.
           Springer, 2005.
           <http://books.google.com/books?id=TTNhSm7HYrIC>

    """
    if hasattr(G, "graph_object"):
        G = G.graph_object

    if wiener_index is None:
        wiener_index = nx.wiener_index(G, weight=weight)

    if node is not None:
        after = nx.wiener_index(G.subgraph(set(G) - {node}), weight=weight)
        return wiener_index - after

    n_cpus = os.cpu_count()
    if abs(n_jobs) > n_cpus:
        n_jobs = n_cpus

    vitality = partial(closeness_vitality, G, weight=weight, wiener_index=wiener_index)
    result = Parallel(n_jobs=n_jobs)(delayed(lambda v: (v, vitality(v)))(v) for v in G)
    return dict(result)
