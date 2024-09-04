import rdflib
import ipycytoscape as cy
import networkx as nx
import pandas as pd

# Funktionsfür die Konvertierung von RDF zu NetworkX
def rdflib_to_networkx(rdf_graph):
    G = nx.DiGraph()  # Use Graph() if you want an undirected graph
    for subj, pred, obj in rdf_graph:
        if isinstance(subj, rdflib.URIRef):
            subj = rdf_graph.qname(subj)
        elif isinstance(subj, rdflib.BNode):
            subj = f"_:bnode_{subj}"  # Convert blank node to a unique string
        pred = rdf_graph.qname(pred)
        if isinstance(obj, rdflib.URIRef):
            obj = rdf_graph.qname(obj)
        elif isinstance(obj, rdflib.BNode):
            obj = f"_:bnode_{obj}"  # Convert blank node to a unique string
        elif isinstance(obj, rdflib.Literal):
            obj = str(obj)  # Convert Literal to its string representation
        G.add_edge(str(subj), str(obj), label=str(pred))
    return G

# Funktionsdefinition, um einen TTL String zu parsen und als Graph zu plotten
def parse_and_plot(ttl_string):
    g = rdflib.Graph()
    g.parse(data = ttl_string)
    nx_graph = rdflib_to_networkx(g)
    plot = cy.CytoscapeWidget()
    plot.graph.add_graph_from_networkx(nx_graph, directed=True)

    style = [
        {
            'selector': 'node',
             'style': {
                'font-family': 'helvetica',
                'font-size': '12px',
                 'color': 'white',
                'text-outline-width': 2,
                'text-outline-color': 'green',
                'background-color': 'green',
                'content': 'data(id)',
                'text-valign': 'center',
             }
        },
        {
            'selector': 'edge.directed',
            'style': {
                'font-family': 'helvetica',
                'font-size': '12px',
                'label': 'data(label)',
                'color': 'white',
                'text-outline-width': 2,
                'text-outline-color': 'orange',
                'background-color': 'orange',
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
            }
        }
    ]
    
    plot.set_style(style)
    return plot

# Funktionsdefinition, um eine Query gegen eine lokale Turtle Datei auszuführen
def query(ttl_string, query_string):
    
    g = rdflib.Graph()
    g.parse(data = ttl_string)

    qres = g.query(query_string)

    df = pd.DataFrame(qres, columns=qres.vars)
    return df