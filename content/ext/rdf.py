import rdflib
import ipycytoscape as cy
import networkx as nx
import pandas as pd
import requests
from IPython.display import HTML
import urllib3

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Funktionsdefinition für die Konvertierung von RDF zu NetworkX
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
def local_query(ttl_string, query_string):
    
    g = rdflib.Graph()
    g.parse(data = ttl_string)

    qres = g.query(query_string)

    df = pd.DataFrame(qres, columns=qres.vars)
    return df

# Funktionsdefinition, um eine SPARQL Query gegen einen SPARQL Endpoint auszuführen
def remote_query(query_string, store="L"):
    """
    Sends a SPARQL query to a SPARQL endpoint and returns the results as a pandas DataFrame.
    
    Parameters:
    - query_string: The SPARQL query string.
    - store: The URL of the SPARQL endpoint (triple store) or some predefined abbrevations.
    
    Returns:
    - A pandas DataFrame containing the query results.
    """
    # Define the headers for the request
    headers = {
        'Accept': 'application/sparql-results+json',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    # three Swiss triplestores
    if store == "F":
        address = 'https://fedlex.data.admin.ch/sparqlendpoint'
    elif store == "G":
        address = 'https://geo.ld.admin.ch/query'
    elif store == "L":
        address = 'https://ld.admin.ch/query'
    else:
        address = store

    # URL-encode the query parameters
    payload = {'query': query_string}
    
    # Send the request to the SPARQL endpoint
    response = requests.post(address, data=payload, headers=headers)

    # Ensure the response uses UTF-8 encoding
    response.encoding = 'utf-8'
    
    # Raise an exception if the request was not successful
    response.raise_for_status()
    
    # Parse the JSON response
    results = response.json()
    
    # Extract the variable names and the data
    columns = results['head']['vars']
    data = [
        {var: binding.get(var, {}).get('value') for var in columns}
        for binding in results['results']['bindings']
    ]
    
    # Create a pandas DataFrame from the data
    df = pd.DataFrame(data, columns=columns)

    # Convert columns to numeric datatype if possible
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except ValueError:
            pass  # Keeps the original data if conversion fails
    
    return df

# Funktionsdefinition, um ein DataFrame als Tabelle mit aktiven HTML Links anzuzeigen
def display_result(df):
    df = HTML(df.to_html(render_links=True, escape=False))
    display(df)
