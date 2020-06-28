## OPTIONS ######
input_name = 'input.csv'
save_name = 'map' #image is saved as html file

fig_width = 1000
fig_height = 600

map_title = 'Unemployment map'
title_font_size = 24
color_scheme = 'inferno'

legend_title = 'Unemployment %' # legend title
legend_font_size = 12
tick_count = 6

show_capitals = True # if True state capitals are shown on the map
show_state_borders = True # if True state borders are drawn on the map

capitals_color = 'white'
borders_color = 'white'

target = 'rate' # the numeric column to show on the map

period_name = 'Period' # (optional) If contained in the data, it is used to filter by period_value
period_value = 'Mar-20' # (optional) only rows where period_name value is equal to period_value are kept
add_period_to_title = True # if True period value is added to legend title
################

import altair as alt
from vega_datasets import data
import numpy as np
import pandas as pd
import pprint as pt

source = pd.read_csv(input_name, dtype={'State FIPS':np.int, 'County FIPS':str, period_name:str, target:np.float64})
keys = list(source.columns.values)
print('Columns: '+str(keys))
source['State FIPS'] = source['State FIPS'].astype(str)
source['id'] = source['State FIPS']+source['County FIPS']

if period_name in keys:
    source = source[source[period_name] == period_value]
    if add_period_to_title:
        legend_title += ' as of '+period_value
        map_title += ' as of '+period_value

counties = alt.topo_feature('https://raw.githubusercontent.com/prikhodkop/county_map/master/us-10m.json', 'counties')

chart = alt.Chart(counties).mark_geoshape().encode(
    color=alt.Color(target+':Q', scale=alt.Scale(scheme=color_scheme), legend=alt.Legend(title=legend_title, tickCount=tick_count)),
    tooltip=target+':N'
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(source, 'id', [target])
).project(
    type='albersUsa'
).properties(
    width=fig_width,
    height=fig_height,
    title= map_title,
)

if show_state_borders:
    states = alt.topo_feature(data.us_10m.url, 'states')

    states_chart = alt.Chart(states).mark_geoshape(
        fill='lightgray',
        fillOpacity=0.0,
        stroke=borders_color,
        strokeWidth=0.5,
    ).properties(
        # title='US State Capitols',
        width=fig_width,
        height=fig_height
    ).project(
        type='albersUsa'
    )

    chart += states_chart

if show_capitals:
    capitals = data.us_state_capitals.url

    base = alt.Chart(capitals).encode(
        longitude='lon:Q',
        latitude='lat:Q',
    )

    text = base.mark_text(dx=7, align='left').encode(
        alt.Text('city', type='nominal'),
        color=alt.value('green'),
        opacity=alt.value(0.8)#alt.condition(~hover, alt.value(0), alt.value(1))
    )

    points = base.mark_point().encode(
        color=alt.value(capitals_color),
        tooltip='city:N',
        size=alt.value(5)#alt.condition(~hover, alt.value(5), alt.value(15))
    )

    chart += points


chart = chart.configure_legend(
    gradientOpacity=0.8,
    gradientDirection='horizontal',
    gradientLength=fig_width,
    orient='bottom',
    titleFontSize=legend_font_size,
    titleAnchor='middle',
    titleLimit=fig_width,
).configure_view(strokeWidth=0).configure_title(fontSize=title_font_size)

from altair_saver import save
save(chart, save_name+'.html')
