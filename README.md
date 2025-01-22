# Graph2Neo4jDB: Import your CSV, build your Neo4j graph, and link nodes—your way!

**#### Graph2Neo4jDB2.0 is a tool for importing CSV file data into a Neo4j database and building your own knowledge graph. It features a simple UI and essential functions (with new features continuously in development).**

## Current Features:

All the features below are supported by a simple UI, so you don't have to write code every time you import your nodes—that's the whole point of this tool.

1. Batch Import for Similar CSVs: Easily import multiple CSV files representing the same node type.
2. Node Relationship Mapping: Establish and customize relationships between nodes.
3. One-Click (Skadoosh) Bulk Import: Import a large set of nodes with configurations and data in a single action.
4. Under Construction... 🚧 (More powerful features coming soon!)### Import your own nodes from csv file

### Import your own nodes from csv file

<img src="images/startAddNode.png" width="500">

**Click the add new node button and you can select your csv data folder and define the node name.**

**The default folder is 'data' inside the project directory.**

<img src="images/selectCsvFolder.png" width="500">

**<span style="color:orange">PS: The folder you select must contain CSV files representing the same type of node. 
For example, if you are importing the 'City' node, your folder might include files like NewYork.csv, Chicago.csv,
etc. The tool will automatically extract the intersection of all column names across the CSV files in the selected folder
and use them as the displayed fields in the UI.</span>**

<img src="images/columnSelect.png" width="500">

**Alright! Now you can drag the column labels you want into the white box on the right. These will be the data fields 
used to construct your nodes. Once you're done, click 'Next' to proceed.**

