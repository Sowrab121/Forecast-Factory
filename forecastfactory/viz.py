import plotly.express as px
import plotly.graph_objects as go

def plot_baseline(df_hist, fc):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_hist['date'], y=df_hist['value'], mode='lines', name='History'))
    fig.add_trace(go.Scatter(x=fc['ds'], y=fc['yhat'], mode='lines', name='Forecast'))
    if 'yhat_lower' in fc and 'yhat_upper' in fc:
        fig.add_traces([
            go.Scatter(x=fc['ds'], y=fc['yhat_upper'], mode='lines', line=dict(width=0), showlegend=False),
            go.Scatter(x=fc['ds'], y=fc['yhat_lower'], fill='tonexty', line=dict(width=0), showlegend=False)
        ])
    fig.update_layout(height=420, margin=dict(l=10,r=10,t=30,b=10))
    return fig

def plot_scenario(baseline, scenario):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=baseline['ds'], y=baseline['yhat'], mode='lines', name='Baseline'))
    fig.add_trace(go.Scatter(x=scenario['ds'], y=scenario['yhat'], mode='lines', name='Scenario'))
    fig.update_layout(height=420, margin=dict(l=10,r=10,t=30,b=10))
    return fig

def plot_delta(scenario):
    fig = px.bar(scenario, x='ds', y='delta')
    fig.update_layout(height=320, margin=dict(l=10,r=10,t=30,b=10))
    return fig
