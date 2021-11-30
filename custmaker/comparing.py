import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from custmaker.making import Customer, KoreanLastname, KoreanFirstname,\
    AgeStat, RegionStat, SexStat


def _percent_format(x, precision):
    return round(x*100, precision)


def _caculate_age(x):
    return datetime.today().year - int(x) + 1


def _draw_sex_compare_plot(conn, customer_df):
    sex_stat_df = pd.read_sql(select(SexStat), conn)
    sex_stat_df.replace({'남': 'Male', '여': 'Female'}, inplace=True)

    sex_grouped = customer_df.groupby('sex')
    customer_sex_df = sex_grouped.size().reset_index()
    customer_sex_df.replace({'남': 'Male', '여': 'Female'}, inplace=True)

    fig = make_subplots(
        rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]]
    )

    fig.add_trace(go.Pie(
         values=sex_stat_df.iloc[:, 1].to_list(),
         labels=sex_stat_df.iloc[:, 0].to_list(),
         domain=dict(x=[0, 0.5]),
         name="Reference", title="Reference", titlefont_size=17),
         row=1, col=1
    )

    fig.add_trace(go.Pie(
         values=customer_sex_df.iloc[:, 1].to_list(),
         labels=customer_sex_df.iloc[:, 0].to_list(),
         domain=dict(x=[0.5, 1.0]),
         name="Actual", title="Actual", titlefont_size=17),
        row=1, col=2
    )

    fig.update_traces(
        textinfo='label+percent', hoverinfo="label+percent+name",
        textfont_size=13, marker=dict(colors=['darkblue', 'red'])
    )
    fig.update_layout(
        showlegend=False, title="Comparison of gender distribution",
        titlefont_size=20, title_font_color='black', title_x=0.5
    )
    fig.show()


def _draw_name_compare_plot(conn, customer_df):
    lastname_df = pd.read_sql(select(KoreanLastname), conn).head(10)
    lastname_df['ratio'] = lastname_df['ratio'].apply(
        _percent_format, args=(2,))
    firstname_df = pd.read_sql(select(KoreanFirstname), conn).head(10)
    firstname_df['ratio'] = firstname_df['ratio'].apply(
        _percent_format, args=(2,))

    customer_lastname_df = customer_df.groupby('lastname').size().reset_index()
    customer_lastname_df.columns = ['lastname', 'count']
    customer_lastname_df.sort_values(by='count', ascending=False, inplace=True)
    customer_lastname_df['ratio'] = round((
        customer_lastname_df['count'] / customer_lastname_df['count'].sum()
    )*100, 2)
    customer_lastname_df = customer_lastname_df.head(10)

    customer_firstname_df = customer_df.groupby('firstname').size().\
        reset_index()
    customer_firstname_df.columns = ['firstname', 'count']
    customer_firstname_df.sort_values(
        by='count', ascending=False, inplace=True
    )
    customer_firstname_df['ratio'] = round((
        customer_firstname_df['count'] / customer_firstname_df['count'].sum()
    )*100, 2)
    customer_firstname_df = customer_firstname_df.head(10)

    fig = make_subplots(
        rows=1, cols=2, subplot_titles=['Reference', 'Actual'],
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    sub_fig1 = px.bar(
        lastname_df, x='lastname', y='ratio', color='ratio', text='ratio',
        labels={'ratio': 'ratio(%)'}
    )
    sub_fig2 = px.bar(
        customer_lastname_df, x='lastname', y='ratio', color='ratio',
        text='ratio', labels={'ratio': 'ratio(%)'}
    )

    fig.add_trace(sub_fig1['data'][0], row=1, col=1)
    fig.add_trace(sub_fig2['data'][0], row=1, col=2)

    fig.update_traces(textfont_size=13, texttemplate='%{text:.2}%')
    fig.update_layout(
        title="Comparison of lastname distribution (Top 10)",
        titlefont_size=20, title_font_color='black', title_x=0.5
    )
    fig.update(layout_coloraxis_showscale=True)
    fig.show()

    fig2 = make_subplots(
        rows=1, cols=2, subplot_titles=['Reference', 'Actual'],
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    sub2_fig1 = px.bar(
        firstname_df, x='firstname', y='ratio', color='ratio', text='ratio',
        labels={'ratio': 'ratio(%)'}
    )
    sub2_fig2 = px.bar(
        customer_firstname_df, x='firstname', y='ratio', color='ratio',
        text='ratio', labels={'ratio': 'ratio(%)'}
    )

    fig2.add_trace(sub2_fig1['data'][0], row=1, col=1)
    fig2.add_trace(sub2_fig2['data'][0], row=1, col=2)

    fig2.update_traces(textfont_size=13, texttemplate='%{text:.2}%')
    fig2.update_layout(
        title="Comparison of firstname distribution (Top 10)",
        titlefont_size=20, title_font_color='black', title_x=0.5
    )
    fig2.update(layout_coloraxis_showscale=True)
    fig2.show()


def _draw_age_compare_plot(conn, customer_df):
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

    fig = make_subplots(
        rows=1, cols=2, subplot_titles=['Reference', 'Actual'],
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    sub_fig1 = px.bar(
        age_stat_df, x='ratio', y='age', orientation='h',
        labels={'ratio': 'ratio(%)'}
    )
    sub_fig2 = px.bar(
        customer_age_df, x='ratio', y='age', orientation='h',
        labels={'ratio': 'ratio(%)'},
    )

    fig.add_trace(sub_fig1['data'][0], row=1, col=1)
    fig.add_trace(sub_fig2['data'][0], row=1, col=2)

    fig.update_traces(textfont_size=13)
    fig.update_layout(
        showlegend=False, title="Comparison of age distribution", height=800,
        titlefont_size=20, title_font_color='black', title_x=0.5
    )
    fig.show()


def show_compare_plot(engine):
    conn = engine.connect()
    customer_df = pd.read_sql(select(Customer), conn)
    _draw_sex_compare_plot(conn, customer_df)
    _draw_name_compare_plot(conn, customer_df)
    _draw_age_compare_plot(conn, customer_df)
