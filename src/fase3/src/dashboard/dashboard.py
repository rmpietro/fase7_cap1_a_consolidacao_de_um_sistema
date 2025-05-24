import oracledb
import json
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from pathlib import Path

# Carregar configuração do banco de dados
config_path = Path(__file__).parent.parent / "config" / "config.json"
with open(config_path) as config_file:
    config = json.load(config_file)

# Função para conectar ao banco e carregar dados da tabela leituras
def load_data():
    with oracledb.connect(
            user=config['user'],
            password=config['password'],
            dsn=config['dsn']
    ) as connection:
        query = """
            SELECT timestamp, temp, humid, P, K, pH, estado_irrigacao
            FROM LEITURAS
            ORDER BY timestamp
        """
        # Lê os dados e converte as colunas para minúsculas
        df = pd.read_sql(query, con=connection)
        df.columns = df.columns.str.lower()  # Convertendo os nomes das colunas para minúsculas
    return df


# Criar o aplicativo Dash
app = Dash(__name__)
app.title = "Dashboard de Leituras de Sensores"

# Carregar os dados

df = load_data()

# Layout do Dashboard
app.layout = html.Div([
    html.H1("Dashboard de Leituras de Sensores"),
    html.Div("Visualização das leituras dos sensores ao longo do tempo, com destaque para o estado de irrigação."),

    dcc.Graph(id="temp_graph"),
    dcc.Graph(id="humid_graph"),
    dcc.Graph(id="phosphorus_graph"),
    dcc.Graph(id="potassium_graph"),
    dcc.Graph(id="ph_graph")
])


# Atualizar gráficos com base nos dados
@app.callback(
    [Output("temp_graph", "figure"),
     Output("humid_graph", "figure"),
     Output("phosphorus_graph", "figure"),
     Output("potassium_graph", "figure"),
     Output("ph_graph", "figure")],
    Input("temp_graph", "id")  # Trigger inicial para carregar os gráficos
)
def update_graphs(_):
    # Temperatura
    fig_temp = px.line(df, x="timestamp", y="temp", color="estado_irrigacao", title="Temperatura ao Longo do Tempo")

    # Umidade
    fig_humid = px.line(df, x="timestamp", y="humid", color="estado_irrigacao", title="Umidade ao Longo do Tempo")

    # Fósforo (p)
    fig_phosphorus = px.line(df, x="timestamp", y="p", color="estado_irrigacao",
                             title="Nível de Fósforo (P) ao Longo do Tempo")

    # Potássio (k)
    fig_potassium = px.line(df, x="timestamp", y="k", color="estado_irrigacao",
                            title="Nível de Potássio (K) ao Longo do Tempo")

    # pH
    fig_ph = px.line(df, x="timestamp", y="ph", color="estado_irrigacao", title="pH ao Longo do Tempo")

    return fig_temp, fig_humid, fig_phosphorus, fig_potassium, fig_ph


# Executar localmente
# if __name__ == "__main__":
#     app.run_server(debug=True)
