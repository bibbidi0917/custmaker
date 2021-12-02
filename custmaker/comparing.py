import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from custmaker.making import Customer, KoreanLastname, KoreanFirstname,\
    AgeStat, RegionStat, SexStat


def _percent_format(x, precision):
    return round(x*100, precision)


def _caculate_age(x):
    return datetime.today().year - int(x) + 1


def _create_compare_plots(conn):
    customer_df = pd.read_sql(select(Customer), conn)

    sex_stat_df = pd.read_sql(select(SexStat), conn)
    sex_stat_df.replace({'남': 'Male', '여': 'Female'}, inplace=True)

    sex_grouped = customer_df.groupby('sex')
    customer_sex_df = sex_grouped.size().reset_index()
    customer_sex_df.replace({'남': 'Male', '여': 'Female'}, inplace=True)

    lastname_df = pd.read_sql(select(KoreanLastname), conn).head(25)
    lastname_df['ratio'] = lastname_df['ratio'].apply(
        _percent_format, args=(2,))
    firstname_df = pd.read_sql(select(KoreanFirstname), conn)
    firstname_df['ratio'] = firstname_df['ratio'].apply(
        _percent_format, args=(2,))

    customer_lastname_df = customer_df.groupby('lastname').size().reset_index()
    customer_lastname_df.columns = ['lastname', 'count']
    customer_lastname_df.sort_values(by='count', ascending=False, inplace=True)
    customer_lastname_df['ratio'] = round((
        customer_lastname_df['count'] / customer_lastname_df['count'].sum()
    )*100, 2)
    customer_lastname_df = customer_lastname_df.head(25)

    customer_firstname_df = customer_df.groupby('firstname').size().\
        reset_index()
    customer_firstname_df.columns = ['firstname', 'count']
    customer_firstname_df.sort_values(
        by='count', ascending=False, inplace=True
    )
    customer_firstname_df['ratio'] = round((
        customer_firstname_df['count'] / customer_firstname_df['count'].sum()
    )*100, 2)

    age_stat_df = pd.read_sql(select(AgeStat), conn)
    age_stat_df['ratio'] = age_stat_df['ratio'].apply(
        _percent_format, args=(2,))
    age_stat_df['age'] = age_stat_df['age'].str[:-1].astype(str)+' years'

    customer_age_df = customer_df['birthdate'].str[:4].apply(_caculate_age)\
        .to_frame()
    customer_age_df.columns = ['age']
    customer_age_df = customer_age_df.groupby('age').size().reset_index()
    customer_age_df.columns = ['age', 'count']
    customer_age_df['ratio'] = round((
        customer_age_df['count'] / customer_age_df['count'].sum()
    )*100, 2)
    customer_age_df['age'] = customer_age_df['age'].astype(str) + ' years'

    sex_fig = make_subplots(
        rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]]
    )

    sex_fig.add_trace(go.Pie(
         values=sex_stat_df.iloc[:, 1].to_list(),
         labels=sex_stat_df.iloc[:, 0].to_list(),
         domain=dict(x=[0, 0.5]),
         name="Reference", title="Reference", titlefont_size=17),
         row=1, col=1
    )

    sex_fig.add_trace(go.Pie(
         values=customer_sex_df.iloc[:, 1].to_list(),
         labels=customer_sex_df.iloc[:, 0].to_list(),
         domain=dict(x=[0.5, 1.0]),
         name="Actual", title="Actual", titlefont_size=17),
        row=1, col=2
    )

    sex_fig.update_traces(
        textinfo='label+percent', hoverinfo="label+percent+name",
        textfont_size=13, marker=dict(colors=['darkblue', 'red'])
    )
    sex_fig.update_layout(
        showlegend=False, title="Comparison of gender distribution",
        titlefont_size=20, title_font_color='black', title_x=0.5
    )

    app = dash.Dash(__name__)

    app.layout = html.Div(style={}, children=[
        html.H1(
            children='Compare reference and actual customer distribution',
            style={
                'textAlign': 'center',
            }
        ),

        dcc.Graph(id='sex-graph', figure=sex_fig),
        dcc.Graph(id='lastname-graph'),
        dcc.Slider(
            id='slider-top_number', min=5, max=25,
            value=5, step=5,
            marks={i: 'Top {}'.format(i) for i in range(5, 30, 5)}
        ),
        dcc.Graph(id='firstname-graph'),
        html.Div([
            "이름을 검색하세요!",
            html.Br(),
            html.Br(),
            dcc.Input(id="firstname-input", type="text", placeholder="ex) 민준"),
            html.Div(id='firstname-output', style={
                'color': 'red', 'font-size': 'large'})
        ], style={'padding-left': '8%'}),
        dcc.Graph(id='age-graph'),
        dcc.RangeSlider(
            id='age-range-slider',
            min=0,
            max=99,
            step=1,
            value=[0, 99],
            marks={i: '{}'.format(i) for i in range(0, 100, 3)}
        ),
        html.Br(),
        html.Div(
            "비교하고 싶은 연령에 마우스를 올려보세요!", style={'textAlign': 'center'}
        ),
        html.Div(id='age-title', style={'textAlign': 'center'}),
        html.Div(
            [dcc.Graph(id='age-compare-graph')],
            style={'padding-left': '36.5%'}
        )
    ])

    @app.callback(
        Output("lastname-graph", "figure"),
        [Input("slider-top_number", "value")]
    )
    def change_top_number(top_number):
        fig = make_subplots(
            rows=1, cols=2, subplot_titles=['Reference', 'Actual'],
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )

        filtered_lastname_df = lastname_df.head(top_number)
        filtered_customer_lastname_df = customer_lastname_df.head(top_number)

        sub_fig1 = px.bar(
            filtered_lastname_df, x='lastname', y='ratio', color='ratio',
            text='ratio', labels={'ratio': 'ratio(%)'}
        )
        sub_fig2 = px.bar(
            filtered_customer_lastname_df, x='lastname', y='ratio',
            color='ratio', text='ratio', labels={'ratio': 'ratio(%)'}
        )

        fig.add_trace(sub_fig1['data'][0], row=1, col=1)
        fig.add_trace(sub_fig2['data'][0], row=1, col=2)

        fig.update_traces(textfont_size=13, texttemplate='%{text:.2}%')
        fig.update_layout(
            title=f"Comparison of lastname distribution (Top {top_number})",
            titlefont_size=20, title_font_color='black', title_x=0.5
        )
        return fig

    @app.callback(
        Output("age-graph", "figure"),
        [Input("age-range-slider", "value")]
    )
    def update_age(age):
        fig = make_subplots(
            rows=1, cols=2, subplot_titles=['Reference', 'Actual'],
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        start_age = age[0]
        end_age = age[1]

        filtered_age_stat_df = age_stat_df[start_age: end_age]

        fig1_color_discrete_sequence = ['#ff7700']*len(filtered_age_stat_df)
        sub_fig1 = px.bar(
            filtered_age_stat_df, x='ratio', y='age', orientation='h',
            labels={'ratio': 'ratio(%)'},
            color_discrete_sequence=fig1_color_discrete_sequence
        )

        filtered_customer_age_df = customer_age_df[start_age: end_age]

        fig2_color_discrete_sequence = ['#00c8ff']*len(
            filtered_customer_age_df)

        sub_fig2 = px.bar(
            filtered_customer_age_df, x='ratio', y='age', orientation='h',
            labels={'ratio': 'ratio(%)'},
            color_discrete_sequence=fig2_color_discrete_sequence
        )

        fig.add_trace(sub_fig1['data'][0], row=1, col=1)
        fig.add_trace(sub_fig2['data'][0], row=1, col=2)

        fig.update_traces(textfont_size=13)
        fig.update_layout(
            showlegend=False, title="Comparison of age distribution",
            titlefont_size=20, title_font_color='black', title_x=0.5,
            height=800
        )
        return fig

    @app.callback(
        Output("age-compare-graph", "figure"),
        Output("age-title", "children"),
        Input("age-graph", "hoverData")
    )
    def update_age_compare_graph(hoverData):
        age = (hoverData['points'][0]['label']
               if hoverData else age_stat_df['age'][0])
        age_title = age

        ref_ratio = age_stat_df[age_stat_df['age'] == age]['ratio'].values[0]
        act_ratio = customer_age_df[customer_age_df['age'] == age]['ratio']\
            .values[0]

        age_compare_df = pd.DataFrame({'category': ['Reference', 'Actual'],
                                       'ratio': [ref_ratio, act_ratio]})

        color_discrete_sequence = ['#ff7700', '#00c8ff']
        fig = px.bar(
            age_compare_df, x='category', y='ratio', text='ratio',
            color='category', labels={'ratio': 'ratio(%)'},
            color_discrete_sequence=color_discrete_sequence
        )
        fig.update_xaxes(title='')
        fig.update_yaxes(title='')
        fig.update_traces(textfont_size=18, texttemplate='%{text:.2}%')
        fig.update_layout(showlegend=False, width=500)

        return fig, age_title

    @app.callback(
        Output("firstname-graph", "figure"),
        Output("firstname-output", "children"),
        Input("firstname-input", "value")
    )
    def update_firstname(firstname):

        fig = make_subplots(
            rows=1, cols=2, subplot_titles=['Reference', 'Actual'],
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        output = ""

        filtered_firstname_df = (
            firstname_df[firstname_df['firstname'] == firstname])
        if len(filtered_firstname_df) == 0:
            filtered_firstname_df = firstname_df.head(20)
            output = "Wrong Name!" if firstname else ""

        filtered_customer_firstname_df = (
            customer_firstname_df[
                customer_firstname_df['firstname'] == firstname])
        if len(filtered_customer_firstname_df) == 0:
            filtered_customer_firstname_df = customer_firstname_df.head(20)

        sub_fig1 = px.bar(
            filtered_firstname_df, x='firstname', y='ratio', color='ratio',
            text='ratio', labels={'ratio': 'ratio(%)'}
        )
        sub_fig2 = px.bar(
            filtered_customer_firstname_df, x='firstname', y='ratio',
            color='ratio', text='ratio', labels={'ratio': 'ratio(%)'}
        )

        fig.add_trace(sub_fig1['data'][0], row=1, col=1)
        fig.add_trace(sub_fig2['data'][0], row=1, col=2)

        fig.update_traces(textfont_size=13, texttemplate='%{text:.2}%')
        fig.update_layout(
            title=f"Comparison of firstname distribution",
            titlefont_size=20, title_font_color='black', title_x=0.5
        )

        return fig, output
    app.run_server(debug=False)


def show_compare_plot(engine):
    conn = engine.connect()
    _create_compare_plots(conn)
