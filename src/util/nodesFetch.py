from py2neo import Graph, Node
import pandas as pd
import streamlit as st


def nodesInNeo4j():
    g = Graph(st.secrets["NEO4J_URI"], auth=(st.secrets["NEO4J_USERNAME"], st.secrets["NEO4J_PASSWORD"]))
    search_query = "MATCH (n) RETURN DISTINCT labels(n) AS labels"
    nodes = []
    labels_result = g.run(search_query).data()
    for record in labels_result:
        if "labels" in record:
            nodes.extend(record["labels"])
    return nodes


def nodeInfoFetch(nodeName):
    g = Graph(st.secrets["NEO4J_URI"], auth=(st.secrets["NEO4J_USERNAME"], st.secrets["NEO4J_PASSWORD"]))
    search_query = f"MATCH (n:{nodeName}) RETURN keys(n) AS properties LIMIT 1"
    info = g.run(search_query).data()[0]["properties"]
    return info

