import logging
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from .sub_agents.sql_agent.tools import sql_agent

logger = logging.getLogger(__name__)

async def call_sql_agent(
    question: str,
    tool_context: ToolContext,
):
    logger.debug("call_sql_agent: %s", question)
    agent_tool = AgentTool(agent=sql_agent)
    
    output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["sql_agent_output"] = output
    return output

async def generate_plot(
    x: list,
    y: list,
    plot_type: str = "bar",
    title: str = "Chart",
    xlabel: str = "X",
    ylabel: str = "Y",
) -> str:
    import plotly.express as px
    import uuid
    import os
    import pandas as pd

    df = pd.DataFrame({'x': x, 'y': y})
    # Ensure y and x is numeric/correct type
    df['y'] = pd.to_numeric(df['y'], errors='coerce').fillna(0)
    
    primary_color = '#6366f1'
    accent_color = '#2dd4bf'
    text_color = '#f8fafc'
    
    if plot_type == 'bar':
        fig = px.bar(df, x='x', y='y', title=title, labels={'x': xlabel, 'y': ylabel}, template='plotly_dark', color='x')
        # fig.update_traces(marker_color=primary_color) # We use color='x' now
    elif plot_type == 'line':
        fig = px.line(df, x='x', y='y', title=title, labels={'x': xlabel, 'y': ylabel}, markers=True, template='plotly_dark')
        fig.update_traces(line_color=accent_color)
    elif plot_type == 'scatter':
        fig = px.scatter(df, x='x', y='y', title=title, labels={'x': xlabel, 'y': ylabel}, template='plotly_dark')
        fig.update_traces(marker_size=12, marker_color='#f472b6')
    elif plot_type == 'pie':
        pie_colors = ['#6366f1', '#ef4444', '#22c55e', '#eab308', '#f97316', '#ec4899', '#06b6d4', '#8b5cf6']
        fig = px.pie(df, names='x', values='y', title=title, template='plotly_dark', color_discrete_sequence=pie_colors)
        fig.update_traces(textposition='inside', textinfo='percent+label')
    else:
        fig = px.bar(df, x='x', y='y', title=title, template='plotly_dark', color='x')

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color=text_color, size=11),
        margin=dict(t=40, l=10, r=10, b=10),
        title_font_size=16,
        showlegend=True,  # Always show legend now that we have colors
        autosize=True
    )

    filename = f"chart_{uuid.uuid4()}.json"
    os.makedirs("app/static/charts", exist_ok=True)
    filepath = f"app/static/charts/{filename}"
    
    fig.write_json(filepath)
    
    return f"![Plotly](/static/charts/{filename})"
