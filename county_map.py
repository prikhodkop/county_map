## OPTIONS ######
name = 'employment_change'

input_name = 'csv/'+name+'.csv'
save_name = 'htmls/'+name #image is saved as html file

fig_width = 1000
fig_height = 600

# map_title = 'Percent of smokers among adults in US as of 2017'
map_title = '      '
title_font_size = 72
color_scheme = 'plasma'
legend_text_color = 'black'
color_ascending = True

hard_upper_bound = None
hard_lower_bound = None

legend_title = ''#'years of potential life lost before age 75 per 100,000 people' # legend title
percents = True
legend_font_size = 20
tick_count = 8

show_capitals = True # if True state capitals are shown on the map
show_state_borders = True # if True state borders are drawn on the map

capitals_color_dot = 'lightgreen'
capitals_color = '#fff'
borders_color = '#fff'
stroke_width = 1

target = 'value' # the numeric column to show on the map

period_name = 'Period' # (optional) If contained in the data, it is used to filter by period_value
period_value = 'Mar-20' # (optional) only rows where period_name value is equal to period_value are kept
add_period_to_title = False # if True period value is added to legend title
################

import altair as alt
from vega_datasets import data
import numpy as np
import pandas as pd
from altair_saver import save

# source = pd.read_csv(input_name, dtype={'State FIPS':np.int, 'County FIPS':str, period_name:str, target:np.float64})
# keys = list(source.columns.values)
# print('Columns: '+str(keys))
# source['State FIPS'] = source['State FIPS'].astype(str)
# source['id'] = source['State FIPS']+source['County FIPS']

source = pd.read_csv(input_name, dtype={'FIPS':'str', target:np.float64}, delimiter=',')
keys = list(source.columns.values)
print('Columns: '+str(keys))

source['id'] = source['FIPS'].apply(lambda x: np.int(x) )

if period_name in keys:
    source = source[source[period_name] == period_value]
    if add_period_to_title:
        legend_title += ' as of '+period_value
        map_title += ' as of '+period_value

counties = alt.topo_feature('https://raw.githubusercontent.com/prikhodkop/county_map/master/us-10m.json', 'counties')

population = pd.read_csv('csv/pop_est2019.csv', dtype={'FIPS':'str', target:np.float64}, delimiter=',')
vet_pop = pd.read_csv('csv/vet_pop.csv', dtype={'FIPS':'str', target:np.float64}, delimiter=',')
#

def calc(rowi):
    try:
        peop = population.loc[population['FIPS'] == rowi['FIPS'], target].iloc[0]
        # if rowi['FIPS'] == '20061':
        #     return np.nan
        result = 10*rowi[target]*vet_pop.loc[vet_pop['FIPS'] == rowi['FIPS'], target].iloc[0]/population.loc[population['FIPS'] == rowi['FIPS'], target].iloc[0]
        return result
    except Exception:
        return np.nan

# source[target] = source.apply(lambda row: calc(row), axis=1)

# source[target] = population[target]

if percents:
    source[target] = source[target].apply(lambda x: np.min([0.35, x/100.]))

# source[target] = source[target].apply(lambda x: np.min((0.6,x)))

upper_bound = np.max(source[target]) if hard_upper_bound is None else hard_upper_bound
lower_bound = np.min(source[target]) if hard_lower_bound is None else hard_lower_bound

chart = alt.Chart(counties).mark_geoshape(
stroke='black',
strokeWidth=0.1,
)
if percents:
    chart = chart.encode(
        color=alt.Color(target+':Q', scale=alt.Scale(domain=[lower_bound, upper_bound], scheme=color_scheme), sort='ascending' if color_ascending else "descending", legend=alt.Legend(format=".0%", title=legend_title, tickCount=tick_count, titleFontSize=legend_font_size))
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
else:
    chart = chart.encode(
        color=alt.Color(target+':Q', scale=alt.Scale(domain=[lower_bound, upper_bound], scheme=color_scheme), sort='ascending' if color_ascending else "descending", legend=alt.Legend(title=legend_title, tickCount=tick_count, titleFontSize=legend_font_size))
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
        strokeWidth=stroke_width,
    ).properties(
        # title='US State Capitols',
        width=fig_width,
        height=fig_height
    ).project(
        type='albersUsa'
    )

    chart += states_chart

    chart2 = alt.Chart(counties).mark_geoshape(fill='lightgray',
    fillOpacity=0.0).encode(
        # tooltip=target+':N'
        tooltip='id:Q'
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

    chart += chart2

if show_capitals:
    cit = pd.read_json('cities.json', dtype={"city":str, "state":str, "lat":np.float64, "lon":np.float64, "rank":np.int, "population":np.int})

    # idxs = cit.groupby(['state'], sort=False)['rank'].transform(min) == cit['rank']#cit[cit['population']>=600000]#data.us_state_capitals.url
    # capitals = cit[idxs]
    capitals = cit[cit['population']>=500000]

    base = alt.Chart(capitals).encode(
        longitude='lon:Q',
        latitude='lat:Q',
    )

    # dys = np.zeros([capitals.shape[0],1])
    text = base.mark_text(dx=7 , align='left').encode(
        alt.Text('city', type='nominal'),
        color=alt.value(capitals_color),
        # opacity=alt.value(1.0)#alt.condition(~hover, alt.value(0), alt.value(1))
    )

    points = base.mark_point().encode(
        color=alt.value(capitals_color_dot),
        tooltip='city:N',
        size=alt.value(5)#alt.condition(~hover, alt.value(5), alt.value(15))
    )

    chart += points + text


chart = chart.configure_legend(
    gradientOpacity=0.8,
    gradientDirection='horizontal',
    gradientLength=fig_width,
    orient='bottom',
    titleFontSize=legend_font_size,
    labelFontSize=legend_font_size,
    titleFontWeight=300,
    # labelFontWeight='300',
    titleAnchor='middle',
    titleLimit=fig_width,
    titleColor=legend_text_color,
    labelColor=legend_text_color
).configure_view(strokeWidth=0).configure_title(fontSize=title_font_size)


save(chart, save_name+'.html')
# save(chart, save_name+'.svg')
