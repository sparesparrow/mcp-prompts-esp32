import plotly.graph_objects as go
import pandas as pd

# Define components and their positions for a cleaner architecture layout
components = {
    'Desktop/Cloud': {
        'main.rs': (1, 7),
        'HTTP API': (2, 7),
        'WebSocket': (3, 7),
        'PostgreSQL': (4, 7),
        'FileSystem': (5, 7)
    },
    'ESP32': {
        'embed/main.rs': (1, 5),
        'WiFi Init': (2, 5),
        'WS Server': (3, 5),
        'LittleFS': (4, 5),
        'Embed Prompts': (5, 5)
    },
    'Shared': {
        'mcp.rs': (1.5, 3),
        'prompt.rs': (3, 3),
        'websocket.rs': (4.5, 3)
    },
    'Build': {
        'export_cat.ts': (1, 1),
        'build_esp32.sh': (2, 1),
        'esp-build.yml': (3, 1),
        'ESP32 Binary': (4, 1)
    },
    'Clients': {
        'Claude Desktop': (0.5, 9),
        'Android': (1.5, 9),
        'PC': (2.5, 9),
        'Port 9000': (3.5, 9),
        'MCP Server': (4.5, 9)
    }
}

# Updated color mapping with better colors
colors_map = {
    'Desktop/Cloud': '#1FB8CD',  # Strong cyan (blue-ish)
    'ESP32': '#FFC185',          # Light orange  
    'Shared': '#5D878F',         # Darker cyan-green (more visible)
    'Build': '#944454',          # Pink-red (purple-ish)
    'Clients': '#D2BA4C'         # Moderate yellow
}

# Create the figure
fig = go.Figure()

# Add component boxes
for category, comps in components.items():
    x_coords = []
    y_coords = []
    component_names = []
    
    for comp_name, (x, y) in comps.items():
        x_coords.append(x)
        y_coords.append(y)
        component_names.append(comp_name)
    
    fig.add_trace(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='markers+text',
        marker=dict(
            size=40,
            color=colors_map[category],
            line=dict(width=2, color='white'),
            symbol='square'
        ),
        text=component_names,
        textposition='middle center',
        textfont=dict(size=9, color='black', family='Arial Black'),
        hovertemplate='<b>%{text}</b><br>Category: ' + category + '<extra></extra>',
        name=category,
        cliponaxis=False
    ))

# Add flow arrows with better positioning
flow_connections = [
    # Desktop/Cloud flow (horizontal)
    {'start': (1, 7), 'end': (2, 7), 'color': '#1FB8CD'},
    {'start': (2, 7), 'end': (3, 7), 'color': '#1FB8CD'},
    {'start': (3, 7), 'end': (4, 7), 'color': '#1FB8CD'},
    {'start': (3, 7), 'end': (5, 7), 'color': '#1FB8CD'},
    
    # ESP32 flow (horizontal)
    {'start': (1, 5), 'end': (2, 5), 'color': '#FFC185'},
    {'start': (2, 5), 'end': (3, 5), 'color': '#FFC185'},
    {'start': (3, 5), 'end': (4, 5), 'color': '#FFC185'},
    {'start': (3, 5), 'end': (5, 5), 'color': '#FFC185'},
    
    # Build pipeline flow
    {'start': (1, 1), 'end': (2, 1), 'color': '#944454'},
    {'start': (2, 1), 'end': (3, 1), 'color': '#944454'},
    {'start': (3, 1), 'end': (4, 1), 'color': '#944454'},
    
    # Client connections to MCP Server
    {'start': (0.5, 9), 'end': (3.5, 9), 'color': '#D2BA4C'},
    {'start': (1.5, 9), 'end': (3.5, 9), 'color': '#D2BA4C'},
    {'start': (2.5, 9), 'end': (3.5, 9), 'color': '#D2BA4C'},
    {'start': (3.5, 9), 'end': (4.5, 9), 'color': '#D2BA4C'},
    
    # Shared component connections (vertical)
    {'start': (1.5, 3), 'end': (1, 7), 'color': '#5D878F'},    # mcp.rs to main.rs
    {'start': (1.5, 3), 'end': (1, 5), 'color': '#5D878F'},    # mcp.rs to embed/main.rs
    {'start': (3, 3), 'end': (3, 7), 'color': '#5D878F'},      # prompt.rs to WebSocket
    {'start': (3, 3), 'end': (3, 5), 'color': '#5D878F'},      # prompt.rs to WS Server
    {'start': (4.5, 3), 'end': (3, 7), 'color': '#5D878F'},    # websocket.rs to WebSocket
    {'start': (4.5, 3), 'end': (3, 5), 'color': '#5D878F'},    # websocket.rs to WS Server
]

# Add connection lines
for conn in flow_connections:
    start, end = conn['start'], conn['end']
    fig.add_trace(go.Scatter(
        x=[start[0], end[0]],
        y=[start[1], end[1]],
        mode='lines',
        line=dict(color=conn['color'], width=2, dash='solid'),
        showlegend=False,
        hoverinfo='skip',
        cliponaxis=False
    ))

# Add directional arrows
arrow_positions = [
    # Desktop flow arrows
    {'pos': (1.5, 7), 'color': '#1FB8CD'},
    {'pos': (2.5, 7), 'color': '#1FB8CD'},
    {'pos': (3.3, 6.8), 'color': '#1FB8CD'},
    {'pos': (3.3, 7.2), 'color': '#1FB8CD'},
    
    # ESP32 flow arrows  
    {'pos': (1.5, 5), 'color': '#FFC185'},
    {'pos': (2.5, 5), 'color': '#FFC185'},
    {'pos': (3.3, 4.8), 'color': '#FFC185'},
    {'pos': (3.3, 5.2), 'color': '#FFC185'},
    
    # Build arrows
    {'pos': (1.5, 1), 'color': '#944454'},
    {'pos': (2.5, 1), 'color': '#944454'},
    {'pos': (3.5, 1), 'color': '#944454'},
    
    # Client arrows
    {'pos': (2, 9), 'color': '#D2BA4C'},
    {'pos': (4, 9), 'color': '#D2BA4C'},
    
    # Shared connection arrows
    {'pos': (1.5, 5), 'color': '#5D878F'},
    {'pos': (1.5, 4), 'color': '#5D878F'},
    {'pos': (3, 5), 'color': '#5D878F'},
    {'pos': (3, 4), 'color': '#5D878F'},
]

for arrow in arrow_positions:
    x, y = arrow['pos']
    fig.add_trace(go.Scatter(
        x=[x], y=[y],
        mode='markers',
        marker=dict(
            size=10,
            color=arrow['color'],
            symbol='triangle-right',
            line=dict(width=1, color='white')
        ),
        showlegend=False,
        hoverinfo='skip',
        cliponaxis=False
    ))

# Update layout with better spacing
fig.update_layout(
    title='mcp-prompts-rs Architecture',
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        title='',
        range=[-0.5, 6]
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        title='',
        range=[0, 10]
    ),
    legend=dict(
        orientation='h', 
        yanchor='bottom', 
        y=1.05, 
        xanchor='center', 
        x=0.5
    ),
    plot_bgcolor='white'
)

# Save the chart
fig.write_image('mcp_architecture.png')