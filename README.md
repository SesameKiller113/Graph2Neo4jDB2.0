# Graph2Neo4jDB: Import your CSV, build your Neo4j graph, and link nodes—your way!

#### **Graph2Neo4jDB2.0 is a tool for importing CSV data into Neo4j and building your own knowledge graph.**

It features a simple UI and essential functions, with new features continuously in development.

## **Current Features**

All features are supported by a simple UI—so you don’t have to write code every time you import nodes.

1. **Batch Import for Similar CSVs** – Import multiple CSV files for the same node type.
2. **Build Node Relationship** – Define and customize relationships between nodes.
3. **One-Click (Skadoosh) Bulk Import** – Import large datasets with just one action.
4. **Under Construction...** 🚧 (More features coming soon!)

---

## 📥 **Import Your Own Node**

### 🛠 **Add a New Node**

Click **"Add New Node"** to select a CSV folder and define the node name.

<img src="images/startAddNode.png" width="400">

📂 **Default Folder:** `'data'` inside the project directory.

<img src="images/selectCsvFolder.png" width="400">

### ⚠️ **Important**



$\textcolor{orange}{The\ selected\ folder\ must\ contain\ CSV\ files\ of\ the\ \textbf{same\ node\ type}.\ For\ example,\ importing\ \textbf{City}\ nodes\ means\ your\ folder\ should\ contain:\ 🗽\ NewYork.csv,\ 🌆\ Chicago.csv,\ etc.\ The\ tool\ automatically\ extracts\ the\ \textbf{common\ column\ names}\ from\ all\ CSVs\ and\ displays\ them\ in\ the\ UI.}$

---

### 🎯 **Select Your Data Fields**

Drag column labels into the **white box** to define node attributes.

After clicking **'Next Step'**, the system will create a folder in `cache/` with the **same name** as your node.
A **`path.json`** file will store the required data paths, enabling **one-click generation** in the future.

⚠ **Check the `cache` folder to avoid duplicate names.**

🔄 **Made a mistake?** Just **drag it out** to remove it.

<img src="images/columnSelect.png" width="400">

---

### 🔗 **Variables Mapping**

This tool allows **renaming CSV columns** as needed.

When selecting a **property key**, ensure it is **globally unique** to avoid overwriting nodes during import.

The tool supports **multiple property keys**, but instead of treating them separately, it **concatenates them** into a single identifier.
For example: **`cityid + cityname = "001newyork"`** (stored as a single `str`).

This new variable is **stored in the node** but does not affect existing data.
⚠ **Property keys are only used for uniqueness during import—you can define them however you prefer.**

<img src="images/columnMapping.png" width="400">

---

### 🚀 **Finalizing Your Import**

Click **Submit**, and the tool will generate **`xxxConfig.json`** in `cache/YourNode/`.

This file **backs up the import configuration**, so you can review or modify it before clicking **Start Import**.

Once a node structure is built, you can **reuse the config file** for **fast imports**, skipping the UI selection process.

---

## 🕸 **Create Node Relationships**

After successfully importing a node, you'll see a newly added, **adorable red node label** on the main page.
You can select **Exactly Two** nodes to create a relationship between them.

<img src="images/afterImport.png" width="400">

Similarly, the tool automatically detects **matching variable names** in both nodes,
allowing you to **customize the relationship name** as needed.

<img src="images/createRelationship.png" width="400">
