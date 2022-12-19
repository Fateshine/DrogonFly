from click import style   # need Dash version 1.21.0 or higher
from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from numpy import False_, append
import pandas as pd
# from fire_sim import Sim_fire2
from sklearn import preprocessing
import math
import numpy as np
from collections import defaultdict
import paho.mqtt.client as mqtt
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from pymongo import MongoClient
from bson import ObjectId
import random
import base64

# -*- coding: utf-8 -*-
from dash import Dash, dcc, html
from sqlalchemy import null
tag_drone = True
tag_task = [True]*3
tag_result = [True]*3
tag_add_task = [True]*3
drone=pd.DataFrame()
drone_status=pd.DataFrame()
Sim=pd.DataFrame()
result = [pd.DataFrame()]*3
task = [pd.DataFrame()]*3
add_task = [pd.DataFrame()]*3
arrow_starting_ratio=0.95
arrow_tip_ratio = 0.1
icon=["fires.png","peoples.png","windows.png"]
color = ["#0D7DDA", "#F1BAD5", "#BAE38E",
         "#F5F3A1", "#EA1616", "#0CDB28", "#E39E0A", "#DA1DC7", "#A230E5", "#ED082A"]
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}
tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px',
    'fontWeight': 'bold'
}
header_style = {"border": "2px black solid", 'backgroundColor': '#119DFF'}
Style2 = {'height': '40%', 'width': '40%'}
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Current Status', children=[
            dbc.Row([
                dbc.Col([
                    dcc.Interval(id='interval_db', interval=2000, n_intervals=0),
                    dcc.Graph(
                        id="current_graph", figure={}
                    )]),
                dbc.Col(
                    dbc.Row([
                            html.P("Drone", style={'margin-top': 200}), dcc.Checklist([{
                                "label": html.Div(
                                    [
                                        html.Img(
                                            src=app.get_asset_url('drone.png'), style=Style2),
                                    ], style={'margin-right': -30}
                                ),
                                "value": "drone",
                            }], id="current_drone", value=["drone"]),

                            # html.P("Tasks", style={'margin-top': 60}),
                            # dcc.Checklist([{
                            #     "label": html.Div(
                            #         [
                            #             html.Img(
                            #                 src=app.get_asset_url('fires.png'), style=Style2),
                            #         ], style={'margin-right': -30}
                            #     ),
                            #     "value": "fire",
                            # },
                            #     {
                            #     "label": html.Div(
                            #         [
                            #             html.Img(
                            #                 src=app.get_asset_url('peoples.png'), style=Style2),
                            #         ], style={'margin-right': -30}
                            #     ),
                            #     "value": "people",
                            # },
                            #     {
                            #     "label": html.Div(
                            #         [
                            #             html.Img(
                            #                 src=app.get_asset_url('windows.png'), style=Style2),
                            #         ], style={'margin-right': -30}
                            #     ),
                            #     "value": "window",
                            # }], inline=True, id="current_task", value=["fire", "people", "window"]),

                            html.P(
                                "Detection Results", style={'margin-top': 60}),
                            dcc.Checklist([{
                                "label": html.Div(
                                    [
                                        html.Img(
                                            src=app.get_asset_url('fires.png'), style=Style2),
                                    ], style={'margin-right': -30}
                                ),
                                "value": "fire",
                            },
                                {
                                "label": html.Div(
                                    [
                                        html.Img(
                                            src=app.get_asset_url('peoples.png'), style=Style2),
                                    ], style={'margin-right': -30}
                                ),
                                "value": "people",
                            },
                                {
                                "label": html.Div(
                                    [
                                        html.Img(
                                            src=app.get_asset_url('windows.png'), style=Style2),
                                    ], style={'margin-right': -30}
                                ),
                                "value": "window",
                            }], inline=True, id="current_detection", value=["fire", "people", "window"])]),
                ),
                dbc.Col([
                    dbc.Row([
                        dbc.Col(html.P("Info"), style={
                            "font-weight": "bold", "font-size": "18px"}),
                        dbc.Col(html.P(id="current_Loc", children="Loc:",
                                style={"font-size": "18px"})),
                        #dbc.Col(html.P("Task",style={"font-size": "20px"})),
                        #dbc.Col(html.P("Detection Results",style={"font-size": "20px"}))
                    ], style={"border": "2px black solid", 'backgroundColor': '#119DFF'}),

                    dbc.Row([
                        dbc.Row([
                            dbc.Col([
                                html.Img(id="result_icon",
                                    src="",style=Style2),
                                html.P(id="current_detection_time", children="detection_time:",
                                       style={"font-size": "20px"}),
                                html.P(id="current_result", children="result:",
                                       style={"font-size": "20px"})
                            ]),
                            dbc.Col(
                                html.Img(id="result_img", src=app.get_asset_url(''))),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Img(
                                    src=""),
                                html.P(children=""),
                                html.P(children="")
                            ]),
                            dbc.Col(
                                html.Img(src="")),
                        ])
                    ], style={"height": '37vh'})], width=4)])
        ], selected_style=tab_selected_style, style=tab_style),
        dcc.Tab(label='Added Tasks', children=[
            dbc.Row([
                dbc.Col(
                    dcc.Graph(
                        figure={}, id="add_graph"
                    )),
                dbc.Col(
                    dbc.Row([
                        html.P("Tasks", style={'margin-top': 200}),
                        dcc.Checklist([{
                            "label": html.Div(
                                [
                                    html.Img(
                                        src=app.get_asset_url('fires.png'), style=Style2),
                                ], style={'margin-right': -30}
                            ),
                            "value": "fire",
                        },
                            {
                            "label": html.Div(
                                [
                                    html.Img(
                                        src=app.get_asset_url('peoples.png'), style=Style2),
                                ], style={'margin-right': -30}
                            ),
                            "value": "people",
                        },
                            {
                            "label": html.Div(
                                [
                                    html.Img(
                                        src=app.get_asset_url('windows.png'), style=Style2),
                                ], style={'margin-right': -30}
                            ),
                            "value": "window",
                        }], inline=True, labelStyle={'display': 'block'}, id="task", value=["fire", "people", "window"]),

                        html.P("New Tasks", style={'margin-top': 60}),  dcc.Checklist([{
                            "label": html.Div(
                                [
                                    html.Img(
                                        src=app.get_asset_url('fires.png'), style=Style2),
                                ], style={'margin-right': -30}
                            ),
                            "value": "fire",
                        },
                            {
                            "label": html.Div(
                                [
                                    html.Img(
                                        src=app.get_asset_url('peoples.png'), style=Style2),
                                ], style={'margin-right': -30}
                            ),
                            "value": "people",
                        },
                            {
                            "label": html.Div(
                                [
                                    html.Img(
                                        src=app.get_asset_url('windows.png'), style=Style2),
                                ], style={'margin-right': -30}
                            ),
                            "value": "window",
                        }], id="add_task1", value=["fire", "people", "window"])])),
                dbc.Col([
                    dbc.Row([
                        dbc.Col(html.P("New Task"), style={
                            "font-weight": "bold"}),
                        dbc.Col(html.P(id="add_loc",children="Loc")),
                        dbc.Col(html.Button(
                            'Add', id='add_btn', n_clicks=0, style={'backgroundColor': '#575757', "color": 'white', 'margin-top': 5})),
                        dbc.Col(html.Button(
                            'Submit', id='submit_btn', n_clicks=0, style={'backgroundColor': '#575757', "color": 'white', 'margin-top': 5}))
                    ], style=header_style),

                    dbc.Row([
                        dbc.Row([
                            dbc.Col(html.P("Task"), style={
                                "border": "2px black solid"}),
                            dbc.Col(html.P("Sig."), style={
                                "border": "2px black solid"}),
                            dbc.Col(html.P("Freq."), style={
                                "border": "2px black solid"}),
                        ], style={'margin-left': 2,  'height': '10vh'}),
                        dbc.Row([
                            dbc.Col(
                                dcc.Checklist([{
                                    "label": html.Div(
                                        [
                                            html.Img(
                                                src=app.get_asset_url('fires.png'), style=Style2),
                                        ], style={'margin-right': -30}
                                    ),
                                    "value": "fire",
                                },
                                    {
                                    "label": html.Div(
                                        [
                                            html.Img(
                                                src=app.get_asset_url('peoples.png'), style=Style2),
                                        ], style={'margin-right': -30}
                                    ),
                                    "value": "people",
                                },
                                    {
                                    "label": html.Div(
                                        [
                                            html.Img(
                                                src=app.get_asset_url('windows.png'), style=Style2),
                                        ], style={'margin-right': -30}
                                    ),
                                    "value": "window",
                                }], id="add_task2"), style={"border": "2px black solid"}),
                            dbc.Col(dcc.Input(id='sig', type='number', value=10, style={"width": "100%"}), style={
                                "border": "2px black solid"}),
                            dbc.Col(dcc.Input(id='freq', type='number', value=10, style={"width": "100%"}), style={
                                "border": "2px black solid"}),
                        ], style={'margin-left': 2,  'height': '10vh'})
                    ]),
                    dbc.Row([
                        dbc.Col(html.P("Task"), style={
                            "font-weight": "bold"}),
                        dbc.Col(html.P(id="del_loc",children="Loc")),
                        dbc.Col(html.Button(
                            'Delete', id='delete_btn', n_clicks=0, style={'backgroundColor': '#575757', "color": 'white', 'margin-top': 5})),
                    ], style=header_style),
                    html.P(id="task_Sig", children="Sig:",
                                       style={"font-size": "20px"}),
                    html.P(id="task_Freq", children="Freq:",
                                       style={"font-size": "20px"})
                    ], width=4)])
        ], selected_style=tab_selected_style, style=tab_style),
        dcc.Tab(label='Prediction', children=[
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="prediction_graph",
                        figure={

                        }
                    )),
                dbc.Col([
                    html.P("Detection Results",style={'margin-top': 200}),
                    dcc.Checklist([{
                        "label": html.Div(
                            [
                                html.Img(
                                    src=app.get_asset_url('fires.png'), style=Style2),
                            ], style={'margin-right': -30}
                        ),
                        "value": "fire",
                    },
                        {
                        "label": html.Div(
                            [
                                html.Img(
                                    src=app.get_asset_url('peoples.png'), style=Style2),
                            ], style={'margin-right': -30}
                        ),
                        "value": "people",
                    },
                        {
                        "label": html.Div(
                            [
                                html.Img(
                                    src=app.get_asset_url('windows.png'), style=Style2),
                            ], style={'margin-right': -30}
                        ),
                        "value": "window",
                    }],id="prediction", value=["fire", "people", "window"])], width={"offset": 1})])

        ], selected_style=tab_selected_style, style=tab_style),
    ])
])


@app.callback(
    Output("current_graph", "figure"),
    Input("current_drone", "value"),
    # Input("current_task", "value"),
    Input("current_detection", "value"),
    Input("interval_db",'n_intervals')
)
def update_picture(drone_tag, detection, n):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    global tag_drone,window1,result,drone_status
    if input_id == "current_drone":
        tag_drone = True if "drone" in drone_tag else False
    # elif input_id == "current_task":
    #     tag_task[0] = True if "fire" in task else False
    #     tag_task[1] = True if "people" in task else False
    #     tag_task[2] = True if "window" in task else False
    elif input_id == "current_detection":
        tag_result[0] = True if "fire" in detection else False
        tag_result[1] = True if "people" in detection else False
        tag_result[2] = True if "window" in detection else False
    elif input_id == "interval_db":
        if len(list(collection_status.find())) >=1 :
            drone_status = pd.DataFrame(list(collection_status.find())).drop_duplicates(subset="Drone",keep="last")
    #     client = MongoClient("mongodb://127.0.0.1:27017/")
    #     mydb = client["Command"]
    #     collection_win = mydb.wins
    #     collection_drone=mydb.drones
    #     window1 = pd.DataFrame(list(collection_win.find()))
    #     drone = pd.DataFrame(list(collection_drone.find()))
    #     result[0] = pd.DataFrame(list(collection_win.find())).query(
    #     'win == "Close" and fire == "Burn" and hum == "None"')
    #     result[1] = pd.DataFrame(list(collection_win.find())).query(
    #     'win == "Close" and fire == "None" and hum == "have"')
    #     result[2] = pd.DataFrame(list(collection_win.find())).query(
    #     'win == "Open" and fire == "None" and hum == "None"')
    # figure = go.Figure()
    # if not drone_sim.empty:
    #     figure = px.scatter_3d(drone_sim, x='x', y='y', z='z', color='Drone', animation_frame='time')
    # else:
    #     figure = go.Figure()
    figure = go.Figure()
    figure.add_trace(go.Mesh3d(x=[32.81,32.81,0,0,32.81,32.81,0,0],y=[58.37,25.56,25.56,58.37,58.37,25.56,25.56,58.37],z=[0,0,0,0,36,36,36,36],alphahull=0,opacity=.2,color="#979595"))
    figure.add_trace(go.Mesh3d(x=[68.38,68.38,3.53,3.53,68.38,68.38,3.53,3.53],y=[25.56,0,0,25.56,25.56,0,0,25.56],z=[0,0,0,0,36,36,36,36],alphahull=0,opacity=.2,color="#979595"))
    customdata = [[row.id] for row in window1.itertuples()]
    figure.add_trace(go.Scatter3d(x=window1["x"], y=window1["y"], z=window1["z"],customdata=customdata,
                                  mode='markers', marker=dict(color="#979595",symbol="square",size=6)))
    if not drone_status.empty:
        figure.add_trace(go.Scatter3d(x=drone_status["x"], y=drone_status["y"], z=drone_status["z"],
                                  mode='markers', marker=dict(size=6,color="#6699CC")))
    if tag_drone and not drone.empty: 
        for i in range(drone["Drone"].idxmax()+1):
            drone_tmp=drone.loc[drone['Drone'] == i].reset_index()
            # figure.add_trace(go.Scatter3d(x=drone_tmp["x"], y=drone_tmp["y"], z=drone_tmp["z"],
            #                             line=dict(width=2,color=f'rgb({np.random.randint(0,256)}, {np.random.randint(0,256)}, {np.random.randint(0,256)})')))
            figure.add_trace(go.Scatter3d(x=drone_tmp["x"], y=drone_tmp["y"], z=drone_tmp["z"],
                                        line=dict(width=2,color="#6699CC")))
            for i in range(drone_tmp.shape[0]-1):
                related_dir_x=drone_tmp["x"][i+1] - drone_tmp["x"][i]
                related_dir_y=drone_tmp["y"][i+1] - drone_tmp["y"][i]
                related_dir_z=drone_tmp["z"][i+1] - drone_tmp["z"][i]
                sum=abs(related_dir_x)+abs(related_dir_y)+abs(related_dir_z)
                if sum <30:
                     global arrow_tip_ratio,arrow_starting_ratio
                     arrow_tip_ratio = 0.5 
                     arrow_starting_ratio=0.8          
                figure.add_trace(go.Cone(
                x=[drone_tmp["x"][i] + arrow_starting_ratio*(related_dir_x)],
                y=[drone_tmp["y"][i] + arrow_starting_ratio*(related_dir_y)],
                z=[drone_tmp["z"][i] + arrow_starting_ratio*(related_dir_z)],
                u=[arrow_tip_ratio*(related_dir_x)],
                v=[arrow_tip_ratio*(related_dir_y)],
                w=[arrow_tip_ratio*(related_dir_z)],
                showlegend=False,
                showscale=False,
                ))
                arrow_tip_ratio=0.1
                arrow_starting_ratio=0.95
    for i in range(3):
        if tag_result[i] and not result[i].empty:
            # customdata = [[result[i]['id'][j], result[i]["detection time"]
            #                [j], result[i]["result"][j],result[i]["img"][j],icon[i]] for j in range(len(result[i]))]
            # customdata=[[row.id,row.accuracy,row.detecton_time,icon[i]] for row in result[i].itertuples()]
            customdata=[[i,i,i,icon[i]] for row in result[i].itertuples()]
            figure.add_trace(go.Scatter3d(x=result[i]["x"], y=result[i]["y"], z=result[i]["z"],customdata=customdata,
                                          mode='markers', marker=dict(color=color[i+4],symbol="square",size=6)))
    figure.update_layout(scene=dict(
        xaxis=dict(nticks=4, range=[-10, 80],),
        yaxis=dict(nticks=4, range=[-30, 70],),
        zaxis=dict(nticks=4, range=[-10, 40],),),
        width=800, height=800, showlegend=False)
    return figure


@app.callback(
    Output('current_Loc', 'children'),
    Output('current_detection_time', 'children'),
    Output('current_result', 'children'),
    # Output('result_img', 'src'),
    Output('result_icon','src'),
    Input('current_graph', 'clickData'))
def update_info(clickdata):
    loc = clickdata["points"][0]["customdata"][0]
    if len(clickdata["points"][0]["customdata"])>2:
        dec = clickdata["points"][0]["customdata"][1]
        accuracy = clickdata["points"][0]["customdata"][2]
        # img_file = clickdata["points"][0]["customdata"][3]
        icon=clickdata["points"][0]["customdata"][3]
    else:
        dec=""
        accuracy=""
        # img_file=""
        icon=""
    return  F"Loc:W{loc}",F"detection time:{dec}", F"raccuracy:{accuracy}" ,app.get_asset_url(icon)


@app.callback(
    Output("add_graph", "figure"),
    Output("add_loc","children"),
    Output("del_loc","children"),
    Output("task_Sig","children"),
    Output("task_Freq","children"),
    Input("task", "value"),
    Input("add_task1", "value"),
    Input("add_btn", "n_clicks"),
    Input("submit_btn","n_clicks"),
    Input("delete_btn","n_clicks"),
    Input('add_graph', 'clickData'),
    State("add_task2", "value"),
    State("sig", "value"),
    State("freq", "value")
)
def update_picture2(task1, add_task1, add_btn,submit_btn,delete_btn, clickdata,add_task2, sig, freq):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    global window2,add_task,task
    id = None 
    task_Sig=None
    task_Freq=None
    if input_id == "task":
        tag_task[0] = True if "fire" in task1 else False
        tag_task[1] = True if "people" in task1 else False
        tag_task[2] = True if "window" in task1 else False
    elif input_id == "add_task1":
        tag_add_task[0] = True if "fire" in add_task1 else False
        tag_add_task[1] = True if "people" in add_task1 else False
        tag_add_task[2] = True if "window" in add_task1 else False
    elif input_id == "add_btn":
        if len(add_task2) <2:
            x = clickdata["points"][0]["x"]
            y = clickdata["points"][0]["y"]
            z = clickdata["points"][0]["z"]
            id = clickdata["points"][0]["customdata"][0]
            if "window" in add_task2:
                event = "win"
                data = pd.DataFrame([[id, x, y, z, event, sig, freq]], columns=[
                                    "id", "x", "y", "z", "event", "sig", "freq"])
                add_task[2]=pd.concat([add_task[2],data])
            elif "fire" in add_task2:
                event = "fire"
                data = pd.DataFrame([[id, x, y, z, event, sig, freq]], columns=[
                                    "id", "x", "y", "z", "event", "sig", "freq"])
                add_task[0]=pd.concat([add_task[0],data])
            elif "people" in add_task2:
                event = "hum"
                data = pd.DataFrame([[id, x, y, z, event, sig, freq]], columns=[
                                    "id", "x", "y", "z", "event", "sig", "freq"])
                add_task[1]=pd.concat([add_task[1],data])
    elif input_id == "submit_btn":
        client = MongoClient("mongodb://140.114.89.210:27017/")
        mydb = client["Command"]
        collection_task = mydb.tasks
        message_content=''
        add_task_tmp=pd.DataFrame()
        for i in range(3):
            if not add_task[i].empty:
                task[i]=pd.concat([task[i],add_task[i]]) 
                add_task_tmp=pd.concat([add_task_tmp,add_task[i]])          
                # collection_task.update_one({'id': id}, {'$set': {'event': data["event"]}})
                collection_task.insert_many(add_task[i].to_dict('records'))
                add_task[i]=add_task[i].iloc[0:0]
        print(add_task_tmp)
        message_content=add_task_tmp.to_json(orient='records')
        print(message_content)
        client_MQTT.publish("Task_add", message_content)
    elif input_id == "delete_btn":
        if len(clickdata["points"][0]["customdata"])>1:
            id = clickdata["points"][0]["customdata"][0]
            tag=clickdata["points"][0]["customdata"][3]
            message_content=''
            if tag<=2:
                client = MongoClient("mongodb://140.114.89.210:27017/")
                mydb = client["Command"]
                collection_task = mydb.tasks
                data=pd.DataFrame(task[tag]['id']==id)
                task[tag]=task[tag].loc[task[tag]['id']!=id]
                collection_task.delete_one({"id":id})
                message_content=data.to_json(orient='records')
                client_MQTT.publish("Task_del", message_content)
            else:
                data=pd.DataFrame(task[tag-3]['id']==id)
                add_task[tag-3]=add_task[tag-3].loc[task[tag-3]['id']!=id]
    elif input_id == "add_graph":
        id = clickdata["points"][0]["customdata"][0]
        if len(clickdata["points"][0]["customdata"])>1:
            task_Sig=clickdata["points"][0]["customdata"][1]
            task_Freq=clickdata["points"][0]["customdata"][2]
    figure = go.Figure()
    figure.add_trace(go.Mesh3d(x=[32.81,32.81,0,0,32.81,32.81,0,0],y=[58.37,25.56,25.56,58.37,58.37,25.56,25.56,58.37],z=[0,0,0,0,36,36,36,36],alphahull=0,opacity=.2,color="#979595"))
    figure.add_trace(go.Mesh3d(x=[68.38,68.38,3.53,3.53,68.38,68.38,3.53,3.53],y=[25.56,0,0,25.56,25.56,0,0,25.56],z=[0,0,0,0,36,36,36,36],alphahull=0,opacity=.2,color="#979595"))
    customdata = [[row.id] for row in window2.itertuples()]
    figure.add_trace(go.Scatter3d(x=window2["x"], y=window2["y"], z=window2["z"],customdata=customdata,
                                  mode='markers', marker=dict(color="#979595",symbol="square",size=6)))

    for i in range(3):
        if tag_task[i] and not task[i].empty:
            customdata = [[row.id,row.sig,row.freq,i] for row in task[i].itertuples()]
            figure.add_trace(go.Scatter3d(x=task[i]["x"], y=task[i]["y"], z=task[i]["z"],customdata=customdata,
                                          mode='markers', marker=dict(color=color[i+4],symbol="square",size=6)))
    for i in range(3):
        if tag_add_task[i] and not add_task[i].empty:
            customdata = [[row.id,row.sig,row.freq,i+3] for row in add_task[i].itertuples()]
            figure.add_trace(go.Scatter3d(x=add_task[i]["x"], y=add_task[i]["y"], z=add_task[i]["z"],customdata=customdata,
                                          mode='markers', marker=dict(color=color[i+1],symbol="square",size=6)))
    figure.update_layout(scene=dict(
        xaxis=dict(nticks=4, range=[-10, 80],),
        yaxis=dict(nticks=4, range=[-30, 70],),
        zaxis=dict(nticks=4, range=[-10, 40],),),
        width=800, height=800, showlegend=False)
    return figure,F"Loc:W{id}",F"Loc:W{id}",F"Sig:{task_Sig}",F"Freq:{task_Freq}"

@app.callback(
    Output("prediction_graph", "figure"),
    Input("prediction", "value"))
def update_prediction(prediction):
    conditions=[]
    values=[]
    if prediction:
        if 'fire' in prediction:
            conditions.append((Sim['fire'] == "Burn"))
            values.append('fire')
        if 'people' in prediction:
            conditions.append((Sim['hum'] == "Have"))
            values.append('hum')
        if 'window' in prediction:
            conditions.append((Sim['win'] == "Open"))
            values.append('window')
        Sim['class'] = np.select(conditions, values,default='None')
    else:
        Sim['class']='None'
    color_discrete_map={'window':color[6],'fire':color[4],'hum':color[5],'None':"#979595"}
    fig = px.scatter_3d(Sim, x='x', y='y', z='z', color='class', animation_frame='time',hover_data=['hum'],color_discrete_map=color_discrete_map)
    fig.update_layout(scene=dict(
        xaxis=dict(nticks=4, range=[-10, 70],),
        yaxis=dict(nticks=4, range=[-10, 70],),
        zaxis=dict(nticks=4, range=[-10, 40],),),
        width=800, height=800)
    return fig

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe([("drone", 0), ("result", 0)])

def on_message(client, userdata, msg):
    global drone,drone_status,Sim
    print(msg.topic+" "+ msg.payload.decode('utf-8'))
    topic=msg.topic
    msg=msg.payload.decode('utf-8').split(",")
    if topic == "Drone Status":
        # new_data=pd.DataFrame([[msg[0], msg[1], msg[2], msg[3]]], columns=["id", "x", "y", "z"])
        # if msg[0] in drone["id"].values:
        #     drone.loc[drone['id']==msg[0]]=new_data
        # else:
        #     drone=pd.concat([drone,new_data])
        drone_status = pd.read_json(msg.payload.decode('utf-8'),orient='records')
        # drone_sim = pd.DataFrame(list(collection_sim.find()))
    elif topic == "Event":
        # new_data=pd.DataFrame([[msg[0], msg[1], msg[2], msg[3]]], columns=["id", "x", "y", "z","event","sig","freq"])
        # if msg[4]=="win":
        #     tag=0
        # elif msg[4]=="fire":
        #     tag=1
        # elif msg[4]=="hum":
        #     tag=2
        # else:
        #     return
        # if msg[0] in result[tag]["id"].values:
        #     result[tag].loc[result[tag]['id']==msg[0]]=new_data
        # else:
        #     result[tag]=pd.concat([result[tag],new_data])
        Sim = pd.DataFrame(list(collection_sim.find()))
        result[0] = pd.DataFrame(list(collection_win.find())).query(
        'win == "Close" and fire == "Burn" and hum == "None"')
        result[1] = pd.DataFrame(list(collection_win.find())).query(
        'win == "Close" and fire == "None" and hum == "have"')
        result[2] = pd.DataFrame(list(collection_win.find())).query(
        'win == "Open" and fire == "None" and hum == "None"')
        # update_fire_sim()
if __name__ == '__main__':
    client = MongoClient("mongodb://140.114.89.210:27017/")
    mydb = client["Command"]
    collection_win = mydb.wins
    collection_tasks= mydb.tasks
    collection_status= mydb.status
    collection_drone= mydb.WPS
    collection_sim = mydb.Simfire
    Sim = pd.DataFrame(list(collection_sim.find()))
    if len(list(collection_drone.find())) >=1 :
        drone = pd.DataFrame(list(collection_drone.find())).drop_duplicates(subset=['Drone','x','y','z'])
    if len(list(collection_status.find())) >=1 :
        drone_status = pd.DataFrame(list(collection_status.find()))
    window1 = pd.DataFrame(list(collection_win.find()))
    window2 = pd.DataFrame(list(collection_win.find()))
    result[0] = pd.DataFrame(list(collection_win.find())).query(
        'win == "Close" and fire == "Burn" and hum == "None"')
    result[1] = pd.DataFrame(list(collection_win.find())).query(
        'win == "Close" and fire == "None" and hum == "Have"')
    result[2] = pd.DataFrame(list(collection_win.find())).query(
        'win == "Open" and fire == "None" and hum == "None"')
    if len(list(collection_tasks.find())) >=1 :
        task[0] = pd.DataFrame(list(collection_tasks.find())).query('event=="fire"')
        task[1] = pd.DataFrame(list(collection_tasks.find())).query('event=="hum"')
        task[2] = pd.DataFrame(list(collection_tasks.find())).query('event=="win"')
   
    client_MQTT = mqtt.Client()
    client_MQTT.on_connect = on_connect
    client_MQTT.on_message = on_message
    client_MQTT.connect("140.114.89.210", 1883)
    client_MQTT.loop_start()
    app.run_server(debug=True)
