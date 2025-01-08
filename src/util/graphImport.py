import json
import os
from py2neo import Graph, Node
import pandas as pd
import streamlit as st


def loadVariable(node_name):
    """
    Load variable configuration based on the node name.

    Args:
        node_name (str): The name of the node to find the corresponding configuration.
    """
    # Define the cache folder path
    cache_folder = os.path.abspath("../cache")
    node_folder = os.path.join(cache_folder, node_name)

    # Define the path to the configuration JSON file
    file_path = os.path.join(node_folder, f"{node_name}Config.json")

    if os.path.exists(file_path) and os.stat(file_path).st_size > 0:
        try:
            # Load the configuration from the JSON file
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

                # Clear cached_data and add the loaded configuration
                cached_data.clear()
                cached_data.append(config_data)

                print("Loaded configuration as dict:", cached_data)
        except json.JSONDecodeError as e:
            print(f"JSON decode error while loading configuration for '{node_name}': {e}")
    else:
        print(f"Configuration file for node '{node_name}' does not exist or is empty.")


def createSingleNode(df, node_config):
    """
    Create nodes based on the node configuration and DataFrame.

    Args:
        df (DataFrame): The DataFrame containing data.
        node_config (dict): The node configuration.

    Returns:
        str: The label of the node.
        str: The property key for merging.
        list: A list of Node objects.
    """
    label = node_config["Node Name"]
    property_key = node_config["Property Key"]

    nodes = []
    for _, row in df.iterrows():
        # Generate unique identifier if property_key has multiple keys
        if len(property_key) > 1:
            unique_identifier = "_".join(str(row[key]) for key in property_key if pd.notnull(row[key]))
            unique_identifier = "score_" + unique_identifier
        else:
            unique_identifier = row[property_key[0]]

        # Construct properties dictionary and include unique_identifier if generated
        properties = {node_config[key]: row[key] for key in row.index if key in node_config and key not in ["Node Name", "Property Key"]}
        if len(property_key) > 1:
            properties["unique_identifier"] = unique_identifier  # Add unique identifier to node properties

        # Create the node with all properties
        node = Node(label, **properties)
        nodes.append(node)
    # Return the unique identifier as the property key if multiple keys were used
    return label, "unique_identifier" if len(property_key) > 1 else node_config[property_key[0]], nodes


def importGraph(graph, csv_files, node_config, progress_callback=None):
    """
    Import data into Neo4j based on the provided configuration and CSV files.

    Args:
        graph (Graph): The Neo4j Graph object.
        csv_files (list): List of CSV file paths.
        node_config (dict): The node configuration.
        progress_callback (function): Callback function to report progress.
    """
    print("Node config:", node_config)
    total_files = len(csv_files)  # Total number of files
    for index, csv_file in enumerate(csv_files):
        try:
            df = pd.read_csv(csv_file)
            print(f"Processing file {index + 1}/{total_files}: {csv_file}, Number of rows: {len(df)}")
            label, property_key, nodes = createSingleNode(df, node_config)
            for node in nodes:
                graph.merge(node, label, property_key)
            print(f"Successfully imported data from {csv_file} into Neo4j.")
        except Exception as e:
            print(f"Failed to process file {csv_file}: {str(e)}")

        if progress_callback:
            progress_callback(index + 1, total_files)


cached_data = []
try:
    g = Graph(st.secrets["NEO4J_URI"], auth=(st.secrets["NEO4J_USERNAME"], st.secrets["NEO4J_PASSWORD"]))
except FileNotFoundError as e:
    print(f"Failed to load secrets: {e}")
    g = None


def startImport(DataFolder, node_name, progress_callback=None):
    """
    Start importing data into Neo4j.

    Args:
        DataFolder (DataFolder): The folder containing CSV files.
        node_name (str): The name of the node.
        progress_callback (function): Callback function to report progress.
    """
    if g is None:
        print("Neo4j connection is not available. Check secrets configuration.")
        return

    loadVariable(node_name)
    print("Cached data:", cached_data)

    if not DataFolder.csv_files_list:
        print("No CSV files found in the provided DataFolder.")
        return

    if not cached_data:
        print("No cached configuration found. Please check data_cache.json.")
        return

    file_paths = DataFolder.csv_files_list
    importGraph(g, file_paths, cached_data[0], progress_callback)

