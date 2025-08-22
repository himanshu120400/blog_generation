import json
import matplotlib.pyplot as plt
import io
from io import BytesIO
import base64
import pandas as pd

def generate_table_md(kpi_data):
    if not kpi_data:
        return "No KPI data available."

    df = pd.DataFrame(kpi_data)
    df = df.fillna("N/A")
    return df.to_markdown(index=False)

def create_kpi_graph(kpi_json):
    try:
        if isinstance(kpi_json, str):
            kpi_data = json.loads(kpi_json)
        else:
            kpi_data = kpi_json

        if not isinstance(kpi_data, (list, dict)):
            raise ValueError("KPI data is not in correct format")

        df = pd.DataFrame(kpi_data)

        plt.figure(figsize=(8, 4))
        df.plot(kind="bar")
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception as e:
        print(f"[ERROR] Could not create KPI graph: {e}")
        return None