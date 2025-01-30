import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import yfinance as yf
import plotly.graph_objs as go

# Initialize Dash app
app = dash.Dash(__name__)

# Store favorites in-memory
favorite_stocks = []

# App layout with Favorites section
app.layout = html.Div(
    style={
        'fontFamily': 'Arial, sans-serif',
        'backgroundColor': '#f4f4f4',
        'padding': '20px',
    },
    children=[
        # Header Section
        html.Div(
            style={
                'textAlign': 'center',
                'marginBottom': '40px',
            },
            children=[
                html.H1(
                    "📈 Stock Market Tracker",
                    style={
                        'color': '#333',
                        'fontSize': '3rem',
                    },
                ),
                html.P(
                    "Track real-time stock performance and save your favorite stocks!",
                    style={
                        'color': '#666',
                        'fontSize': '1.2rem',
                    },
                ),
            ],
        ),
        # Input Section
        html.Div(
            style={
                'maxWidth': '600px',
                'margin': '0 auto',
                'textAlign': 'center',
            },
            children=[
                dcc.Input(
                    id='stock-input',
                    type='text',
                    placeholder='Enter Stock Symbol (e.g., AAPL, TSLA)',
                    debounce=True,
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'border': '1px solid #ccc',
                        'borderRadius': '5px',
                        'fontSize': '1rem',
                    },
                ),
                html.Button(
                    'Save to Favorites',
                    id='save-button',
                    n_clicks=0,
                    style={
                        'marginTop': '10px',
                        'padding': '10px 20px',
                        'backgroundColor': '#007BFF',
                        'color': '#fff',
                        'border': 'none',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'fontSize': '1rem',
                    },
                ),
            ],
        ),
        # Graph Section
        html.Div(
            style={
                'marginTop': '40px',
            },
            children=[
                dcc.Graph(
                    id='stock-chart',
                    style={
                        'border': '1px solid #ccc',
                        'borderRadius': '10px',
                        'backgroundColor': '#fff',
                        'padding': '20px',
                    },
                ),
            ],
        ),
        # Favorites Section
        html.Div(
            style={
                'marginTop': '40px',
                'maxWidth': '600px',
                'margin': '0 auto',
                'padding': '20px',
                'backgroundColor': '#fff',
                'borderRadius': '10px',
                'border': '1px solid #ccc',
            },
            children=[
                html.H2(
                    "⭐ Favorite Stocks",
                    style={
                        'color': '#333',
                        'fontSize': '1.5rem',
                        'textAlign': 'center',
                    },
                ),
                html.Ul(
                    id='favorites-list',
                    style={
                        'listStyleType': 'none',
                        'padding': '0',
                        'margin': '0',
                        'color': '#007BFF',
                        'cursor': 'pointer',
                        'fontSize': '1.2rem',
                        'textAlign': 'center',
                    },
                ),
            ],
        ),
    ],
)

# Callback to update the graph
@app.callback(
    Output('stock-chart', 'figure'),
    [Input('stock-input', 'value'),
     Input('favorites-list', 'n_clicks')],
    [State('favorites-list', 'children')]
)
def update_graph(stock_symbol, n_clicks, favorite_children):
    # Check if the user clicked on a favorite stock
    if n_clicks and favorite_children:
        stock_symbol = favorite_children[n_clicks - 1]['props']['children']

    if not stock_symbol:
        # Default chart if no stock symbol is entered
        figure = go.Figure(
            layout=go.Layout(
                title="Enter a stock symbol to view the data!",
                title_x=0.5,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                annotations=[
                    dict(
                        text="Start by typing a stock symbol above.",
                        xref="paper",
                        yref="paper",
                        showarrow=False,
                        font=dict(size=16),
                    )
                ],
            )
        )
        return figure

    try:
        # Fetch stock data
        stock_data = yf.Ticker(stock_symbol)
        df = stock_data.history(period='1mo')  # Last month data

        # Create the line chart
        figure = go.Figure(
            data=[go.Scatter(x=df.index, y=df['Close'], mode='lines', name=stock_symbol)],
            layout=go.Layout(
                title=f"{stock_symbol.upper()} Stock Prices (Last 1 Month)",
                title_x=0.5,
                xaxis=dict(title='Date', showgrid=True),
                yaxis=dict(title='Close Price (USD)', showgrid=True),
                plot_bgcolor='#f9f9f9',
                paper_bgcolor='#ffffff',
                font=dict(family="Arial, sans-serif", size=14),
            )
        )
        return figure

    except Exception as e:
        # Handle errors gracefully
        figure = go.Figure(
            layout=go.Layout(
                title="Error Fetching Data",
                title_x=0.5,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                annotations=[
                    dict(
                        text="Unable to fetch stock data. Check the symbol and try again.",
                        xref="paper",
                        yref="paper",
                        showarrow=False,
                        font=dict(size=16, color='red'),
                    )
                ],
            )
        )
        return figure

# Callback to handle saving to favorites
@app.callback(
    Output('favorites-list', 'children'),
    Input('save-button', 'n_clicks'),
    State('stock-input', 'value'),
    prevent_initial_call=True
)
def save_to_favorites(n_clicks, stock_symbol):
    global favorite_stocks

    # Validate input and prevent duplicates
    if stock_symbol and stock_symbol.upper() not in favorite_stocks:
        favorite_stocks.append(stock_symbol.upper())

    # Render the updated list of favorite stocks
    return [html.Li(stock, id=f'favorite-{i}') for i, stock in enumerate(favorite_stocks)]

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
