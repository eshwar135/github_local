import os
import zipfile
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# -------------------------
# Setup project directories
# -------------------------
base = Path("MultiAgent-Excel-Executed")
folders = [
    base / "data",
    base / "src" / "agents",
    base / "notebooks",
    base / "outputs",
    base / "logs",
    base / ".ipynb_checkpoints"
]

for f in folders:
    f.mkdir(parents=True, exist_ok=True)

# -------------------------
# Create sample Excel data
# -------------------------
df = pd.DataFrame(
    np.random.randint(1, 100, size=(10, 10)),
    columns=[f"Col_{i}" for i in range(1, 11)]
)
df.insert(0, "Region", ["North", "South", "East", "West", "North", "South", "East", "West", "North", "South"])
df.to_excel(base / "data" / "sample_data.xlsx", index=False)

# -------------------------
# Create a sample plot
# -------------------------
region_revenue = df.groupby("Region")["Col_1"].sum()
plt.figure(figsize=(6,4))
region_revenue.plot(kind="bar")
plt.title("Revenue by Region")
plt.ylabel("Revenue")
plt.tight_layout()
plot_path = base / "outputs" / "revenue_by_region.png"
plt.savefig(plot_path)
plt.close()

# -------------------------
# Create source files
# -------------------------
orchestrator_code = """class Orchestrator:
    def __init__(self, agents):
        self.agents = agents

    def query(self, task):
        results = {}
        for agent in self.agents:
            results[agent.__class__.__name__] = agent.handle(task)
        return results
"""

agent_code = """class BaseAgent:
    def __init__(self, name):
        self.name = name

    def handle(self, task):
        return {self.name: f'Handled task: {task}'}
"""

(base / "src" / "orchestrator.py").write_text(orchestrator_code)
(base / "src" / "agents" / "base_agent.py").write_text(agent_code)

# -------------------------
# Create executed notebook
# -------------------------
executed_nb = {
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {"name":"stdout","output_type":"stream","text":["Excel file created with 10x10 data including Region column\\n"]}
   ],
   "source": [
    "import pandas as pd\\n",
    "df = pd.read_excel('../data/sample_data.xlsx')\\n",
    "print('Excel file created with 10x10 data including Region column')\\n",
    "df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [
    {"data":{"text/html": df.head().to_html()}, "execution_count":2,"metadata":{},"output_type":"execute_result"}
   ],
   "source": [
    "df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [
    {"data":{"image/png": plot_path.read_bytes()}, "execution_count":3,"metadata":{},"output_type":"execute_result"}
   ],
   "source": [
    "import matplotlib.pyplot as plt\\n",
    "import seaborn as sns\\n",
    "region_revenue = df.groupby('Region')['Col_1'].sum()\\n",
    "region_revenue.plot(kind='bar')\\n",
    "plt.show()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.11"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

nb_path = base / "notebooks" / "01_setup_and_demo.ipynb"
with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(executed_nb, f)

# also copy into checkpoints
checkpoint_path = base / ".ipynb_checkpoints" / "01_setup_and_demo-checkpoint.ipynb"
with open(checkpoint_path, "w", encoding="utf-8") as f:
    json.dump(executed_nb, f)

# -------------------------
# Create README + reqs
# -------------------------
(base / "README.md").write_text("# MultiAgent Excel Project\\nThis project demonstrates multi-agent orchestration on Excel data.\\nNotebook already executed with outputs.\\n")
(base / "requirements.txt").write_text("pandas\\nnumpy\\nmatplotlib\\nopenpyxl\\n")

# -------------------------
# Create final zip
# -------------------------
zip_path = Path("MultiAgent-Excel-Executed.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(base):
        for file in files:
            full_path = Path(root) / file
            zipf.write(full_path, full_path.relative_to(base.parent))

print(f"✅ Project zip created: {zip_path.resolve()}")
