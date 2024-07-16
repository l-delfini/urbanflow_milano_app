import numpy as np
import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from shapely.wkt import loads
import shapely
import asyncio
from contextlib import contextmanager
import datetime

from bokeh.themes.theme import Theme
from bokeh.models import HoverTool


st.set_page_config(page_title="UrbanFlow Milano", page_icon="🔀️", layout='wide', initial_sidebar_state='expanded')
st.sidebar.title("🔀 UrbanFlow Milano")


def introduction():
    st.title('🔀 UrbanFlow Milano ')
    with st.container():
        st.write(
            "UrbanFlow Milano is an interactive web application created with Streamlit as part of a university project. The goal is to experiment with and present different ways of visualizing data related to sustainable mobility. The application is designed for desktop use and is divided into four pages: Introduction, OD Flow Map, Trajectory Flow Map, and Chord Diagram.")

        st.write(
            "The data displayed is provided by Fluctuo and concerns trips made using shared mobility means in the municipality of Milan during July 2023. The respective NILs were assigned to the starting and ending geographical coordinates, in order to be able to have an aggregation of the trips. To optimize performance, the app only shows a sample of the complete data. The information displayed is therefore not sufficient to draw definitive conclusions on Milan's mobility. However, the app can provide valuable insights into technologies and forms of interaction useful for future projects")
        with st.expander("**What are NILs?**"):
            st.write(
                "NILs, or Nuclei di Identità Locale, are a territorial subdivision of the City of Milan introduced with the Piano di Governo del Territorio (PGT) 2030. They total 88 and represent the smallest planning units established by the plan.")

        st.header('Overview')

        st.markdown('''
    
            - [OD Flow Map](#od-flow-map)
            - [Trajectory Flow Map](#trajectory-flow-map)
            - [Chord Diagram](#chord-diagram)
            ''', unsafe_allow_html=True)

        st.subheader('OD Flow map')
        st.image('img/tutorial1.png',
                 caption='Sidebar for filter selection (A); popup (B) with ranking of top 3 incoming and outgoing connections.',
                 use_column_width='auto')
        st.write(
            "The OD flow map is a useful tool for visualizing the interconnections between different NILs. The main elements in the sidebar and visualization panel are listed below.")
        st.markdown('''



#### Sidebar:
- **Filter links:** This option allows you to choose whether to filter incoming or outgoing connections.
- **Maximum number of Incoming/Outgoing links:** limits the number of links that originate from or arrive at each individual node. To avoid visual clutter, the default value is set to 3.
- **Minimum link opacity:** Allows you to customize the minimum opacity of the links, with a default value of 0.05.

#### Visualization Panel:
- **Arrows:** Each arrow represents a connection between two NILs. The color of the arrow is determined by the origin node, and the thickness of the arrow is proportional to the amount of flow.
- **Points:** Each NIL is represented by a colored point, positioned at the coordinates of its centroid.
- **Popup:** Clicking on a node displays a popup window showing the top three incoming and outgoing connections, based on the selected tab.
                ''', unsafe_allow_html=True)

        st.write("---")
        st.subheader('Trajectory Flow map')
        st.image('img/tutorial2.png',
                 caption='Sidebar to filter data and generate map (A); legend with vehicle type filter (B).',
                 use_column_width='auto')
        st.write(
            "The Trajectory Map is a useful tool for displaying the trajectories of trips that have the selected NIL as their source or destination. The main elements in the sidebar and display panel are listed below.")
        st.markdown("""
#### Sidebar:
- **Select a NIL:** Allows you to choose the NIL whose trips you want to view.
- **Flow Direction:** Allows you to choose whether to view trips entering or exiting the selected NIL.
- **Time range:** Allows you to customize the time range of the displayed data. You can specify start and end dates and times. 
- **Map style:** Allows you to customize the appearance of the map. Available options include dark, light, satellite and open-street-map. 
#### Visualization Panel:

- **Lines:** The lines represent the routes of the trips. The color indicates the type of vehicle used, while the opacity reflects the amount.
- **Legenda:** The legend shows the correspondence between colors and types of vehicles. By clicking on one of the items, you can filter the view.
                    """)
        st.write("---")
        st.subheader('Chord Diagram')
        st.image('img/tutorial3.png',
                 caption="Sidebar for setting filters (A); tab for choosing the view (B).",
                 use_column_width='auto')
        st.write(
            "The Chord Diagram is a circular graph that highlights relationships between entities by means of arcs of varying sizes. In this specific visualization, the nodes (points on the edge) represent NILs, while the arcs indicate the number of trips made.")
        st.markdown("""
        #### Sidebar:
        - **Which vehicles do you want to display?:** This option allows you to select the type of vehicles to display in the graph.
        - **Minimum number of trips between two NILs:** This option allows you to display only those links that have a number of links equal to or greater than the selected number.
        #### Visualization Panel:
        - **Tab:** This option allows you to switch between the graph view and the corresponding table view, providing more precise details about the number of trips between the NILs. 
        - **Arcs:** The arcs represent the connections between the NILs. Their color indicates the origin node, while their width highlights the volume of exchange.
        - **Points:** Each point represents a NIL and is identifiable by a specific color.
        """)
        placeholder.empty()


def print_map():
    with st.sidebar:
        trip_direction = st.radio(
            "Filter link:",
            ["Incoming", "Outgoing"])

        if trip_direction == 'Outgoing':
            trip_direction_m = 'Start'
        else:
            trip_direction_m = 'End'


        max_connection = st.slider('Maximum number of ' + trip_direction + ' links', 0, 73, 3,
                        help="The limit is applied to all NILs on the map.")
        opaq_min = st.slider("Minimum link opacity", 0.0,
                                1.0,
                                0.05, help="Increase the opacity to make links with few trips visible.")

    st.title('OD Flow Map')

    trip = pd.read_csv('trip.csv')
    trip = trip[trip['Start'] != trip['End']]

    origins_popup = trip.sort_values(by=['Start', 'total'], ascending=[True, False])

    destinations_popup = trip.sort_values(by=['End', 'total'], ascending=[True, False])

    origins_popup = origins_popup.groupby('Start').head(3)

    destinations_popup = destinations_popup.groupby('End').head(3)

    trip = trip.sort_values(by=[trip_direction_m, 'total'], ascending=[True, False])

    trip = trip.groupby(trip_direction_m).head(max_connection)

    nil_area = pd.read_csv('nil_milano.csv')

    result = trip.groupby(trip_direction_m)['total'].sum()

    nil_area.dropna()
    nil_area['viaggi'] = nil_area['NIL'].map(result)

    nil_area['viaggi'] = (nil_area['viaggi'].fillna(0))
    nil_area = nil_area[nil_area['viaggi'] > 0]
    total_trip = sum(nil_area['viaggi'])
    nil_area['colors'] = ["#580000", "#5d0500", "#681101", "#711b03", "#7b2406", "#832d09", "#8c350b", "#943d0f",
                         "#9b4411", "#a34b14", "#ab5217", "#b25a19", "#b9601c", "#bf681e", "#c66f21", "#cc7522",
                         "#d37b25", "#d98127", "#dd892f", "#e0913d", "#e2984a", "#e4a055", "#e6a760", "#e7ae6a",
                         "#e9b573", "#ebbc7d", "#edc287", "#eec890", "#efcd99", "#f1d3a1", "#f2d8a7", "#f3ddae",
                         "#f5e1b6", "#f6e5bc", "#f7eac1", "#f8edc7", "#f9f1cc", "#faf4d0", "#fbf6d3", "#fcf8d8",
                         "#fdfbdb", "#fdfcdc", "#fdfddd", "#fefede", "#ffffe0", "#fdfedf", "#fcfdde", "#fbfcde",
                         "#f9fbdd", "#f6fadd", "#f3f9dc", "#f0f6db", "#edf4da", "#e9f2d9", "#e3efd7", "#dfecd6",
                         "#dae9d4", "#d4e6d2", "#cfe3d0", "#c9dfce", "#c1dbca", "#bbd7c8", "#b4d3c5", "#accfc2",
                         "#a3cbbe", "#9cc7bc", "#92c2b8", "#88beb5", "#7dbab2", "#72b5af", "#63b1ab", "#53aca8",
                         "#42a8a6", "#3ba1a0", "#389a99", "#359392", "#328c8b", "#2f8585", "#2c7e7e", "#287777",
                         '#b53a37', '#bf681e',"#ffffe0","#dfecd6","#9cc7bc","#f5e1b6"][0:len(nil_area)]

    def popup_html(row):
        nil_name = nil_area['NIL'][row]

        tot_origins = []
        tot_destinations = []
        origins = []
        destinations = []

        for index, row in (origins_popup[origins_popup['Start'] == nil_name]).iterrows():
            origins.append(row['End'])
            tot_origins.append(row['total'])

        for index, row in (destinations_popup[destinations_popup['End'] == nil_name]).iterrows():
            destinations.append(row['Start'])
            tot_destinations.append(row['total'])

        len_check_origins = len(origins)
        len_check_destinations = len(destinations)


        html = """
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
    
<h4 style="margin-bottom:10">{}</h4>""".format(nil_name) + """
  <ul  class="nav nav-tabs" >
    <li class="nav-link active" id="nav-home-tab" data-bs-toggle="tab" data-bs-target="#nav-home" type="button" role="tab" aria-controls="nav-home" aria-selected="true">Origins</li>
    <li class="nav-link" id="nav-profile-tab" data-bs-toggle="tab" data-bs-target="#nav-profile" type="button" role="tab" aria-controls="nav-profile" aria-selected="false">Destinations</li>
  </ul>
<div class="tab-content" id="nav-tabContent">
  <div style="opacity:1" class="tab-pane show active" id="nav-home" role="tabpanel" aria-labelledby="nav-home-tab">
    <table >
<thead style="border: 1px solid #E1E4E9;">
    <tr style="background-color:#F7F9FD; color:#464F60">
      <th style="border-right:1px solid #E1E4E9; padding:8px">Ranking</th>
      <th style="padding:8px;border-right:1px solid #E1E4E9;">Origins</th>
      <th style="padding:8px">No. Trip</th>
    </tr>
  </thead>
<tr style="background-color:white; border-width: 0 1px 0 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#1</td>
<td style="padding:8px">{}</td>""".format(destinations[0] if len_check_destinations > 0 else '//') + """
<td style="padding:8px">{}</td>""".format(tot_destinations[0] if len_check_destinations > 0 else '//') + """
</tr>
<tr style="background-color:#F9FAFC; border-width: 0 1px 0 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#2</td>
<td style="padding:8px">{}</td>""".format(destinations[1] if len_check_destinations > 1 else '//') + """
<td style="padding:8px">{}</td>""".format(tot_destinations[1] if len_check_destinations > 1 else '//') + """
</tr>
<tr style="background-color:white; border-width: 0 1px 1px 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#3</td>
<td style="padding:8px">{}</td>""".format(destinations[2] if len_check_destinations > 2 else '//') + """
<td style="padding:8px">{}</td>""".format(tot_destinations[2] if len_check_destinations > 2 else '//') + """
</tr>
</table>
  </div>
  <div style="opacity:1" class="tab-pane " id="nav-profile" role="tabpanel" aria-labelledby="nav-profile-tab">
    <table>
<thead style="border: 1px solid #E1E4E9;">
    <tr style="background-color:#F7F9FD; color:#464F60">
      <th style="border-right:1px solid #E1E4E9; padding:8px">Ranking</th>
      <th style="padding:8px;border-right:1px solid #E1E4E9;">Destinations</th>
      <th style="padding:8px">No. Trips</th>
    </tr>
  </thead>
<tr style="background-color:white; border-width: 0 1px 0 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#1</td>
<td style="padding:8px">{}</td>""".format(origins[0] if len_check_origins > 0 else '//') + """
<td style="padding:8px">{}</td>""".format(tot_origins[0] if len_check_destinations > 0 else '//') + """
</tr>
<tr style="background-color:#F9FAFC; border-width: 0 1px 0 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#2</td>
<td style="padding:8px">{}</td>""".format(origins[1] if len_check_origins > 1 else '//') + """
<td style="padding:8px">{}</td>""".format(tot_origins[1] if len_check_origins > 1 else '//') + """
</tr>
<tr style="background-color:white; border-width: 0 1px 1px 1px; border-style:solid; border-color:#E1E4E9;">
<td style="padding:8px">#3</td>
<td style="padding:8px">{}</td>""".format(origins[2] if len_check_origins > 2 else '//') + """
<td style="padding:8px">{}</td>""".format(tot_origins[2] if len_check_origins > 2 else '//') + """
</tr>
</table>
  </div>
</div>"""
        return html


    m = folium.Map(zoom_start=14, location=(45.467250, 9.189686),
                   tiles="https://api.mapbox.com/styles/v1/mapbox/dark-v10/tiles/{z}/{x}/{y}?access_token=",
                   attr="Mapbox")
    m.get_root().html.add_child(folium.JavascriptLink('https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.min.js'))

  #The following code for generating arrows is taken from https://statesmigrate.streamlit.app/

    for index, row in trip.iterrows():
        selected_row = nil_area[nil_area['NIL'] == row['Start']]
        opaq = 100 * (row['total'] / int(total_trip))
        opaq = max(opaq_min, opaq)
        color = selected_row['colors'].to_list()

        poly = folium.PolyLine(trip=[[row['x_Start'], row['y_Start']],
                                          [row['x_End'], row['y_End']]], opacity=opaq, color=color)

        poly.add_to(m)
        l = 0.0014  # the arrow length
        widh = 0.000042  # 2*widh is the width of the arrow base as triangle

        A = np.array([row['x_Start'], row['y_Start']])
        B = np.array([row['x_End'], row['y_End']])

        v = B - A

        w = v / np.linalg.norm(v)
        u = np.array([-w[1], w[0]]) * 10  # u orthogonal on  w

        P = B - l * w
        S = P - widh * u
        T = P + widh * u

        pointA = (S[0], S[1])
        pointB = (T[0], T[1])
        pointC = (B[0], B[1])

        points = [pointA, pointB, pointC, pointA]

        folium.PolyLine(locations=points, opacity=opaq, fill=True, color=color).add_to(m)

    for index1, row1 in nil_area.iterrows():
        html = popup_html(index1)
        popup = folium.Popup(folium.Html(html, script=True), max_width=500)
        folium.Circle(location=[row1['quartieri_centroidi_X'], row1['quartieri_centroidi_Y']], color='black',
                      weight=0.6, fill_opacity=1, fill_color=[row1['colors']], radius=50, popup=popup).add_to(m)

    st.info("""The map shows the centroids of Nuclei di Identità Locale (NILs) and their connections. The data refer to trips made in July 2023 using shared car-sharing services, bicycles, scooters, and moped.
        """, icon="ℹ️")

    m.save("prova.html")
    HtmlFile = open("prova.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height=600, scrolling=True)


def display_map():
    st.title('Trajectory Flow Map')
    import plotly.express as px
    import geopandas as gpd

    st.info("""The trajectory flow map shows the trajectory of trips that have the selected NIL as their origin or destination. The data refer to a sample of trips made in July 2023 using car-sharing services, shared bicycles, scooters, and moped.
                    """, icon="ℹ️")

    df_milano = gpd.read_file('milan_trips.csv')
    with st.sidebar:
        with st.form("my_form"):
            option = st.selectbox('Select a NIL', (df_milano['End'].unique()), index=40)
            direction = st.radio("Flow direction", ["Incoming", "Outgoing"], index=0)
            start_date = datetime.date(2023, 7, 1)
            end_date = datetime.date(2023, 7, 1)
            with st.expander("Time interval"):
                date = st.date_input("Date", (start_date, end_date), min_value=start_date, )
                time_start = st.time_input('Start time', datetime.time(0, 0), )
                time_end = st.time_input('End time', datetime.time(23, 59))
            map_style = st.selectbox('Map style', ['dark', 'light', 'satellite', 'open-street-map'], index=0)
            submitted = st.form_submit_button("Generate map")

    if submitted:
        if direction == 'Incoming':
            flow = 'End'
        else:
            flow = 'Start'

        df_milano = df_milano[df_milano[flow] == option]

        date_time_start = datetime.datetime.combine(date[0], time_start)
        date_time_end = datetime.datetime.combine(date[1], time_end)

        df_milano['local_ts_start'] = pd.to_datetime(df_milano['local_ts_start'])
        df_milano['local_ts_end'] = pd.to_datetime(df_milano['local_ts_end'])
        df_milano = df_milano[
            (df_milano['local_ts_start'] >= date_time_start) & (df_milano['local_ts_end'] <= date_time_end)]
        df_milano['geom_wkt_estimated_route'] = df_milano['geom_wkt_estimated_route'].apply(loads)

        df_milano = gpd.GeoDataFrame(df_milano, geometry='geom_wkt_estimated_route', crs='EPSG:4326')
        exploded = df_milano.explode('geom_wkt_estimated_route')

        exploded = exploded.sort_values(by='type_vehicle')

        lats = []
        lons = []
        names = []
        vehicles = []
        for feature, name, vehicle in zip(exploded.geometry, exploded.id, exploded.type_vehicle):
            if isinstance(feature, shapely.geometry.linestring.LineString):
                linestrings = [feature]
            elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
                linestrings = feature.geoms
            else:
                continue
            for linestring in linestrings:
                x, y = linestring.xy
                lats = np.append(lats, y)
                lons = np.append(lons, x)
                names = np.append(names, [name] * len(y))
                vehicles = np.append(vehicles, [vehicle] * len(y))
                lats = np.append(lats, None)
                lons = np.append(lons, None)
                names = np.append(names, None)
                vehicles = np.append(vehicles, None)

        newnames = {'C': 'Car (C)', 'B': 'Bike (B)', 'M': 'Moped (M)', 'S': 'Scooter (S)'}

        fig = px.line_mapbox(lat=lats, lon=lons,
                             mapbox_style=map_style, line_group=names, color=vehicles,
                             labels={'line_group': 'ID', 'color': 'Vehicle', },color_discrete_map={
                                 "C": "#FE2B2B",
                                 "B": "#7EEFA1",
                                 "M": "#84C9FF",
                                 "S": "#FFABAB", } )

        fig.update_layout(mapbox_zoom=10, legend_title_text='Vehicle', height=634, legend=dict(
            yanchor="top",
            orientation='h',
            y=1.05,
            xanchor="left",
            x=0)
                          , margin=dict(
                l=0,
                r=0,
                b=0,
                t=0,

            ))
        fig.update_mapboxes(
            accesstoken="pk.eyJ1IjoiZGVsZm8xIiwiYSI6ImNsbmx1YzB6MzJwNDgya3JsZzJsZjc1YWwifQ.6nVOkmTdDbEXbOPu3twfwA")
        fig.update_traces(opacity=0.6)

        fig.for_each_trace(lambda t: t.update(name=newnames[t.name]))
        st.plotly_chart(fig, use_container_width=True, height=634)


def chord_diagram():
    st.title('Chord Diagram')

    # Create a context manager to run an event loop
    @contextmanager
    def setup_event_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            yield loop
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    # Use the context manager to create an event loop
    with setup_event_loop() as loop:
        import holoviews as hv


    with st.sidebar:

        options = st.multiselect(
            'Which vehicles do you want to visualize?',
            ['Bikes', 'Cars', 'Scooters', 'Mopeds'],
            ['Bikes', 'Cars', 'Scooters', 'Mopeds']

        )
        viaggi_min = st.slider('Minimum number of trips between two NILs', 20, 75, 30)

    dictionary_opts = {
        'Bikes': 'B',
        'Cars': 'C',
        'Scooters': 'M',
        'Mopeds': 'S'
    }
    lista_input = []

    for i in options:
        lista_input.append(dictionary_opts[i])

    hv.extension('bokeh')

    census_data = pd.read_csv('nuovo_dataframe2.csv')
    census_data = census_data[census_data['Start'] != census_data['End']]

    filtered_df = census_data[census_data['Viaggi'] >= viaggi_min]

    filtered_df = filtered_df[filtered_df['type_vehicle'].isin(lista_input)]

    filtered_df = filtered_df.drop(columns='type_vehicle')

    filtered_df = filtered_df.groupby(['Start', 'End'])['Viaggi'].sum().reset_index()
    colonna_unique = set(filtered_df['Start'])
    colonna_unique.update(filtered_df['End'])
    colonna_unique = list(colonna_unique)

    with st.container():
        st.info("""The diagram provides a visual representation of the connections between NILs. The data refer to a sample of trips made in July 2023 using shared car-sharing services, bicycles, scooters, and mopeds.
                        """, icon="ℹ️")

    n = 0
    dictionary = {}
    for i in colonna_unique:
        dictionary[i] = n
        n += 1

    links = filtered_df.replace({'Start': dictionary,
                                 'End': dictionary})

    nodes = pd.DataFrame({'index': dictionary.values(), 'name': dictionary.keys()})

    # filtered_df.rename(columns={"Viaggi": "values"})

    theme = Theme(
        json={
            'attrs': {
                'figure': {

                    'border_fill_color': '#0F1116',

                },
            }
        })

    hv.renderer('bokeh').theme = theme

    nodes = hv.Dataset(nodes, 'index')

    chord = hv.Chord((links, nodes))
    tooltips = [('NIL', '@name')]

    hover = HoverTool(tooltips=tooltips)

    chord.opts(cmap='viridis', edge_cmap='viridis', edge_color="Start", labels="name", node_color="index",
               height=600, width=600, tools=[hover, 'tap'])

    hv.save(chord, 'fig.html')
    HtmlFile = open("fig.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()

    tab1, tab2, = st.tabs(["Chord Diagram", "Filtered trips table"])

    with tab1:

        components.html("<style>:root {background-color: #0F1116;}</style>"+ source_code, height=600,)

    with tab2:

        st.dataframe(filtered_df)



page_names_to_funcs = {
    "Introduction": introduction,
    "OD Flow Map": print_map,
    "Trajectory Flow Map": display_map,
    "Chord Diagram": chord_diagram,
}
selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())

with st.sidebar:
    placeholder = st.empty()
    placeholder.write("""
                     #### Visualization setup""")

page_names_to_funcs[selected_page]()
