import platform
import plotly
from  plotly import graph_objects as go
from plotly.offline import download_plotlyjs, plot
import networkx as nx

def make_annotations(Xn, Yn, labels, font_size=14, font_color='rgb(10,10,10)'):
    L=len(Xn)
    if len(labels)!=L:
        raise ValueError('The lists pos and text must have the same len')
    annotations = []
    for k in range(L):
        annotations.append(dict(text=labels[k], 
                                x=Xn[k]+0.00015, 
                                y=Yn[k]+0.00015,#this additional value is chosen by trial and error
                                xref='x1', yref='y1',
                                font=dict(color= font_color, size=font_size),
                                showarrow=False)
                          )
    return annotations  

def create_visuals(test_name):
    f = open("Sites.txt", 'r')

    temp_sites = f.read()
    temp_sites = temp_sites.split("\n")
    temp_sites.pop()
    sites = []
    for site in temp_sites:
        site = site.split(", ")
        site[0] = int(site[0])
        site[1] = float(site[1])
        site[2] = float(site[2])
        site[3] = int(site[3])
        sites.append(site)


    f = open("Flows.txt", 'r')
    temp_flows = f.read()
    temp_flows = temp_flows.split("\n")
    temp_flows.pop()
    flows = []
    for flow in temp_flows:
        flow = flow.split(", ")
        flow[0] = int(flow[0])
        flow[1] = int(flow[1])
        flow[2] = float(flow[2])
        flow[3] = float(flow[3])
        flows.append(flow)

    midpoints = []
    for flow in flows:
        x0 = sites[flow[0]][1]
        y0 = sites[flow[0]][2]
        x1 = sites[flow[1]][1]
        y1 = sites[flow[1]][2]
        temp_length = flow[2]
        new_x = (x0 + x1) / 2
        new_y = (y0 + y1) / 2
        midpoints.append([temp_length, new_x, new_y])

    Xm = [midpoints[k][1] for k in range(len(midpoints))]
    Ym = [midpoints[k][2] for k in range(len(midpoints))]
    flow_lengths = ["This: " + str(flows[k][2]) + "\t Upstream: " + str(flows[k][3]) for k in range(len(flows))]
    midpoint_trace = go.Scatter(
        x=Xm, y=Ym,
        mode='markers',
        text = flow_lengths,
        hoverinfo='text',
        marker=go.Marker(
            opacity=0
        )
    )


    G=nx.Graph()
    my_nodes = range(len(sites))
    my_edges = [(flows[k][0],flows[k][1]) for k in range(len(flows))]
    G.add_nodes_from(my_nodes)
    G.add_edges_from(my_edges)

    Xn = [sites[k][1] for k in range(len(sites))]
    Yn = [sites[k][2] for k in range(len(sites))]
    labels = [sites[k][0] for k in range(len(sites))]
    node_labels = ["ID: " + str(sites[k][0]) + "\nAssigned ID: " + str(sites[k][3]) for k in range(len(sites))]

    node_trace = go.Scatter(
        x=Xn, y=Yn,
        mode='markers',
        text = node_labels,
        hoverinfo = 'text',
        marker=dict(
            color = 'white',
            size=7,
            line_width=2))

    Xe = []
    Ye = []
    for e in G.edges():
        x0 = Xn[e[0]]
        y0 = Yn[e[0]]
        x1 = Xn[e[1]]
        y1 = Yn[e[1]]
        Xe.append(x0)
        Xe.append(x1)
        Xe.append(None)
        Ye.append(y0)
        Ye.append(y1)
        Ye.append(None)

    edge_trace = go.Scatter(
        x=Xe, y=Ye,
        line=dict(width=0.5, color='#888'),
        mode='lines')

    axis=dict(showline=False, # hide axis line, grid, ticklabels and  title
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title='' 
            )
    layout=dict(title= test_name,  
                font= dict(family='Balto'),
                width=1500,
                height=1000,
                autosize=False,
                showlegend=False,
                xaxis=axis,
                yaxis=axis,
        hovermode='closest',
        plot_bgcolor='#bad7ff', #set background color            
        )

    fig = dict(data=[node_trace, edge_trace, midpoint_trace], layout=layout)
    fig['layout'].update(annotations=make_annotations(Xn, Yn, labels))
    plot(fig)

