import pandas as pd
import plotly.express as px
import plotly.io as pio

# Data
data = {"priority": ["Kritické", "Střední", "Rychlé"], "count": [10, 8, 3]}
df = pd.DataFrame(data)

# Create bar chart
fig = px.bar(
    df,
    x="priority",
    y="count",
    text="count",
    labels={"priority": "Priorita", "count": "Počet souborů"},
    title="HID USB soubor priority",
    color="priority",
    color_discrete_sequence=["#1FB8CD", "#FFC185", "#ECEBD5"],
)

# Styling per rules
fig.update_traces(textposition='outside')
fig.update_layout(showlegend=False)

# Save figure
file_path = "hid_usb_priority.png"
fig.write_image(file_path)
file_path