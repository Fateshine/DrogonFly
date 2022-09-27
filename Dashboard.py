from click import style   # need Dash version 1.21.0 or higher
from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from numpy import False_, append
import pandas as pd
from fire_sim import Sim_fire2
import numpy as np
from collections import defaultdict
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
drone = pd.DataFrame()
result = [pd.DataFrame()]*3
task = [pd.DataFrame()]*3
add_task = [pd.DataFrame()]*3
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
                    dcc.Interval(id='interval_db', interval=30000, n_intervals=0),
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
def update_picture(drone, detection,n_intervals):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    global tag_drone,window1,result
    if input_id == "current_drone":
        tag_drone = True if "drone" in drone else False
    # elif input_id == "current_task":
    #     tag_task[0] = True if "fire" in task else False
    #     tag_task[1] = True if "people" in task else False
    #     tag_task[2] = True if "window" in task else False
    elif input_id == "current_detection":
        tag_result[0] = True if "fire" in detection else False
        tag_result[1] = True if "people" in detection else False
        tag_result[2] = True if "window" in detection else False
    elif input_id == "interval_db":
        client = MongoClient("mongodb://127.0.0.1:27017/")
        mydb = client["Command"]
        collection_win = mydb.wins
        window1 = pd.DataFrame(list(collection_win.find()))
        drone = pd.DataFrame(list(collection_win.find())).query(
        'win == "Close" and fire == "None" and hum == "None"')
        result[0] = pd.DataFrame(list(collection_win.find())).query(
        'win == "Close" and fire == "Burn" and hum == "None"')
        result[1] = pd.DataFrame(list(collection_win.find())).query(
        'win == "Close" and fire == "None" and hum == "have"')
        result[2] = pd.DataFrame(list(collection_win.find())).query(
        'win == "Open" and fire == "None" and hum == "None"')
    figure = go.Figure()
    customdata = [[row.id] for row in window1.itertuples()]
    figure.add_trace(go.Scatter3d(x=window1["x"], y=window1["y"], z=window1["z"],customdata=customdata,
                                  mode='markers', marker=dict(color="#979595")))
    # if tag_drone and not drone[i].empty: 
    #     figure.add_trace(go.Scatter3d(x=drone["x"], y=drone["y"], z=drone["z"],
    #                                   mode='markers', marker=dict(color=color[i])))
    for i in range(3):
        if tag_result[i] and not result[i].empty:
            # customdata = [[result[i]['id'][j], result[i]["detection time"]
            #                [j], result[i]["result"][j],result[i]["img"][j],icon[i]] for j in range(len(result[i]))]
            customdata=[[i,i,i,"",icon[i]] for j in range(len(result[i]))]
            figure.add_trace(go.Scatter3d(x=result[i]["x"], y=result[i]["y"], z=result[i]["z"],customdata=customdata,
                                          mode='markers', marker=dict(color=color[i+4])))
    figure.update_layout(scene=dict(
        xaxis=dict(nticks=4, range=[-10, 70],),
        yaxis=dict(nticks=4, range=[-10, 70],),
        zaxis=dict(nticks=4, range=[-10, 40],),),
        width=800, height=800, showlegend=False)
    return figure


@app.callback(
    Output('current_Loc', 'children'),
    Output('current_detection_time', 'children'),
    Output('current_result', 'children'),
    Output('result_img', 'src'),
    Output('result_icon','src'),
    Input('current_graph', 'clickData'))
def update_info(clickdata):
    loc = clickdata["points"][0]["customdata"][0]
    if len(clickdata["points"][0]["customdata"])>2:
        dec = clickdata["points"][0]["customdata"][1]
        result = clickdata["points"][0]["customdata"][2]
        img_file = clickdata["points"][0]["customdata"][3]
        icon=clickdata["points"][0]["customdata"][4]
    else:
        dec=""
        result=""
        img_file=""
        icon=""
    return  F"Loc:W{loc}",F"detection time:{dec}", F"result:{result}",app.get_asset_url(img_file) ,app.get_asset_url(icon)


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
                data = pd.DataFrame([[x, y, z, event, id, sig, freq]], columns=[
                                    "x", "y", "z", "event", "id", "sig", "freq"])
                add_task[2]=pd.concat([add_task[2],data])
            elif "fire" in add_task2:
                event = "fire"
                data = pd.DataFrame([[x, y, z, event, id, sig, freq]], columns=[
                                    "x", "y", "z", "event", "id", "sig", "freq"])
                add_task[0]=pd.concat([add_task[0],data])
            elif "people" in add_task2:
                event = "hum"
                data = pd.DataFrame([[x, y, z, event, id, sig, freq]], columns=[
                                    "x", "y", "z", "event", "id", "sig", "freq"])
                add_task[1]=pd.concat([add_task[1],data])
    elif input_id == "submit_btn":
        client = MongoClient("mongodb://127.0.0.1:27017/")
        mydb = client["Command"]
        collection_task = mydb.tasks
        for i in range(3):
            if not add_task[i].empty:
                task[i]=pd.concat([task[i],add_task[i]])           
                # collection_task.update_one({'id': id}, {'$set': {'event': data["event"]}})
                collection_task.insert_many(add_task[i].to_dict('records'))
                add_task[i]=add_task[i].iloc[0:0]
    elif input_id == "delete_btn":
        if len(clickdata["points"][0]["customdata"])>1:
            id = clickdata["points"][0]["customdata"][0]
            tag=clickdata["points"][0]["customdata"][3]
            if tag<=2:
                client = MongoClient("mongodb://127.0.0.1:27017/")
                mydb = client["Command"]
                collection_task = mydb.tasks
                data=pd.DataFrame(task[tag]['id']==id)
                task[tag]=task[tag].loc[task[tag]['id']!=id]
                collection_task.delete_one({"id":id})
            else:
                data=pd.DataFrame(task[tag-3]['id']==id)
                add_task[tag-3]=add_task[tag-3].loc[task[tag-3]['id']!=id]
    elif input_id == "add_graph":
        id = clickdata["points"][0]["customdata"][0]
        if len(clickdata["points"][0]["customdata"])>1:
            task_Sig=clickdata["points"][0]["customdata"][1]
            task_Freq=clickdata["points"][0]["customdata"][2]
    figure = go.Figure()
    customdata = [[row.id] for row in window2.itertuples()]
    figure.add_trace(go.Scatter3d(x=window2["x"], y=window2["y"], z=window2["z"],customdata=customdata,
                                  mode='markers', marker=dict(color="#979595")))
    for i in range(3):
        if tag_task[i] and not task[i].empty:
            customdata = [[row.id,row.sig,row.freq,i] for row in task[i].itertuples()]
            figure.add_trace(go.Scatter3d(x=task[i]["x"], y=task[i]["y"], z=task[i]["z"],customdata=customdata,
                                          mode='markers', marker=dict(color=color[i+4])))
    for i in range(3):
        if tag_add_task[i] and not add_task[i].empty:
            customdata = [[row.id,row.sig,row.freq,i+3] for row in add_task[i].itertuples()]
            figure.add_trace(go.Scatter3d(x=add_task[i]["x"], y=add_task[i]["y"], z=add_task[i]["z"],customdata=customdata,
                                          mode='markers', marker=dict(color=color[i+1])))
    figure.update_layout(scene=dict(
        xaxis=dict(nticks=4, range=[-10, 70],),
        yaxis=dict(nticks=4, range=[-10, 70],),
        zaxis=dict(nticks=4, range=[-10, 40],),),
        width=800, height=800, showlegend=False)
    return figure,F"Loc:W{id}",F"Loc:W{id}",F"Sig:{task_Sig}",F"Freq:{task_Freq}"

@app.callback(
    Output("prediction_graph", "figure"),
    Input("prediction", "value"))
def update_prediction(prediction):
    client = MongoClient("mongodb://127.0.0.1:27017/")
    mydb = client["Command"]
    collection = mydb.Simfire
    df = pd.DataFrame(list(collection.find()))
    conditions=[]
    values=[]
    if prediction:
        if 'fire' in prediction:
            conditions.append((df['fire'] == "Burn"))
            values.append('fire')
        if 'people' in prediction:
            conditions.append((df['hum'] == "Have"))
            values.append('hum')
        if 'window' in prediction:
            conditions.append((df['win'] == "Open"))
            values.append('window')
        df['class'] = np.select(conditions, values,default='None')
    else:
        df['class']='None'
    color_discrete_map={'window':color[6],'fire':color[4],'hum':color[5],'None':"#979595"}
    fig = px.scatter_3d(df, x='x', y='y', z='z', color='class', animation_frame='time',hover_data=['hum'],color_discrete_map=color_discrete_map)
    fig.update_layout(scene=dict(
        xaxis=dict(nticks=4, range=[-10, 70],),
        yaxis=dict(nticks=4, range=[-10, 70],),
        zaxis=dict(nticks=4, range=[-10, 40],),),
        width=800, height=800)
    return fig

def Get_sim(st,et, rseed,a,output,time_slot):  # here a is a window!!!!! 
    lay_num=12
    Sim_fire2(st,et,rseed,a,output,time_slot)  # write the simulation in a file.
    Timeline=pd.read_csv(output,sep='/ ',engine='python')
    Sim=defaultdict(dict)
    Sim_real=defaultdict(dict)
    win=[]
    firs=list(Timeline['f'])
    tmp=[i[1:-1].split(', ') for i in firs]
    all_fire=set()
    for i in tmp:
        try:
            all_fire.update([int(k) for k in i])
        except:
            pass
    hum_floors=set([i//lay_num for i in all_fire]+[i//lay_num +1 for i in all_fire])
    fire_floors=set([i//lay_num for i in all_fire])  
    win_floors=set([i//lay_num for i in all_fire]+[i//lay_num -1 for i in all_fire])  # this layer and the lower layer. 
    #print(f"ss {all_floors}")
    for index,row in Timeline.iterrows():
        #print(row)
        tmp=row['f'][1:-1].split(', ')
        tmps=row['f_s'][1:-1].split(', ')
        #print(f"check  {tmp}")
        if len(tmp)==1 and tmp[0]=='':
            Sim[row['t']]['f']=[]
            Sim_real[row['t']]['f']=[]
            Sim[row['t']]['f_s']=[]
            Sim_real[row['t']]['f_s']=[]
        else:
            fire=[int(tmp[i]) for i in range(len(tmp))]
            fire_state=[int(tmps[i]) for i in range(len(tmp))]
            Sim[row['t']]['f']=fire
            Sim[row['t']]['f_s']=fire_state
            Sim_real[row['t']]['f']=fire
            Sim_real[row['t']]['f_s']=fire_state
        tmp=row['w'][1:-1].split(', ')
        #if len(tmp)>0:
        winn=[int(tmp[i]) for i in range(len(tmp))]
        win=[]
        for i in winn:
            if i//lay_num in win_floors: # 
                win.append(i)
        Sim[row['t']]['w']=win
        Sim_real[row['t']]['w']=win
        #except:
            #Sim[row['t']]['w']=[]
        tmp=row['h'][1:-1].split(', ')
        tmps=row['h_s'][1:-1].split(', ')
        try:
            humm=[int(tmp[i]) for i in range(len(tmp))]
            hum_s=[int(tmps[i]) for i in range(len(tmp))]
            h_s=dict(zip(humm,hum_s))
            hum=[];state=[]
            for i in humm:
                if i//lay_num in hum_floors:
                    hum.append(i)
                    state.append(h_s.get(i))
            Sim[row['t']]['h']=hum 
            Sim[row['t']]['h_s']=state
            Sim_real[row['t']]['h']=hum
            Sim_real[row['t']]['h_s']=state
        except:
            Sim[row['t']]['h']=[]
            Sim[row['t']]['h_s']=[]
            Sim_real[row['t']]['h_s']=[]
            Sim_real[row['t']]['h']=[]     
    return Sim,Sim_real,fire_floors, hum_floors, win_floors
def update_fire_sim():
    floor_num=12
    va=3
    rooms_d=pd.read_csv('../data/rooms.csv',sep=',')
    room_AF=dict(zip(list(rooms_d['r']),(zip(list(rooms_d['w']),list(rooms_d['d'])))))
    all_room=len(room_AF)*floor_num
    ii=0
    time_slot=1
    random.seed(ii)
    a=random.sample(range(all_room),va) #fire source 
    output=f"./result/dash/sim_{ii}.csv"
    Sim,Sim_real,fire_floors,hum_floors,win_floors=Get_sim(0,60,ii,a,output,time_slot)
    client = MongoClient("mongodb://127.0.0.1:27017/")
    # Create database called animals
    mydb = client["Command"]
    # Create Collection (table) called shelterA
    collection = mydb.Simfire
    windows=pd.read_csv('../data/all_win.csv',sep=' ')
    collection.delete_many({})
    for key, item in Sim.items():
        for index, row in windows.iterrows():
                if row["id"]in item['f']:
                    record={"time": key, "id":row["id"], "x":row["v_1_x"], "y":row["v_1_y"], 
                          "z":row["v_1_z"], 'win': 'Close', 'fire': 'Burn', 'hum': 'None'}
                elif row["id"]in item['h']:
                    record={"time": key, "id":row["id"], "x":row["v_1_x"], "y":row["v_1_y"], 
                          "z":row["v_1_z"], 'win': 'Close', 'fire': 'None', 'hum': 'Have'}
                elif row["id"]in item['w']:
                    record={"time": key, "id":row["id"], "x":row["v_1_x"], "y":row["v_1_y"], 
                          "z":row["v_1_z"], 'win': 'Open', 'fire': 'None', 'hum': 'None'}
                else: 
                    record={"time": key, "id":row["id"], "x":row["v_1_x"], "y":row["v_1_y"], 
                          "z":row["v_1_z"], 'win': 'Close', 'fire': 'None', 'hum': 'None'}
                collection.insert_one(record)
    return
if __name__ == '__main__':
    client = MongoClient("mongodb://127.0.0.1:27017/")
    mydb = client["Command"]
    collection_win = mydb.wins
    collection_tasks=mydb.tasks
    window1 = pd.DataFrame(list(collection_win.find()))
    window2 = pd.DataFrame(list(collection_win.find()))
    result[0] = pd.DataFrame(list(collection_win.find())).query(
        'win == "Close" and fire == "Burn" and hum == "None"')
    result[1] = pd.DataFrame(list(collection_win.find())).query(
        'win == "Close" and fire == "None" and hum == "have"')
    result[2] = pd.DataFrame(list(collection_win.find())).query(
        'win == "Open" and fire == "None" and hum == "None"')
    if len(list(collection_tasks.find())) >=1 :
        task[0] = pd.DataFrame(list(collection_tasks.find())).query('event=="win"')
        task[1] = pd.DataFrame(list(collection_tasks.find())).query('event=="fire"')
        task[2] = pd.DataFrame(list(collection_tasks.find())).query('event=="hum"')
    app.run_server(debug=True)