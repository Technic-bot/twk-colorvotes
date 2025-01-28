import pandas as pd
import argparse
import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
import numpy as np
import sys

votes='number of votes'
name='sketch names'
tk_blue = "#72CDFE"
tk_orange = "#F7941D"
def proc_opts():
    parser = argparse.ArgumentParser(description="Color vote visualization")
    parser.add_argument("filename")
    parser.add_argument("--graph-out")
    parser.add_argument("--dry-run", action='store_true')
    return parser.parse_args()

def read_file(filename):
    df = pd.read_excel(filename)
    print(f"Df size {len(df)}")
    df['date'] = pd.to_datetime(df['month vote'], format="%B, %Y")
    # df.drop('posted date', inplace=True, axis=1)
    df.dropna(axis='index', inplace=True, subset=votes)
    print(f"Df after proccessing: {len(df)}")
    return df

def make_histogram(df):
    fig, ax = plt.subplots(figsize = (9, 9))
    bins = np.linspace(10,110,11)
    hist, edges = np.histogram(df[votes], bins)
    #ax.bar(hist, edges, rwidth= 0.9, color="#72CDFE")
    ax.hist(edges[:-1], edges, weights=hist, rwidth= 0.9, color="#72CDFE")

    ax.set_title("Votes histogram")
    ax.set_xlabel("Votes")
    ax.set_ylabel("Frequency")

    ax.set_xticks(edges)
    ax.tick_params(axis='x', rotation=45)

    return fig

def group_timeseries(df):
    #boolean_slice = df['date'] < pd.to_datetime(datetime.date(2018, 1, 1))
    gp = pd.Grouper(key='date', freq='MS')
    gp_df = df.groupby(gp)
    votes_over_time = gp_df[votes].sum()
    #print(votes_over_time.loc['2024-01-1':'2024-12-30'])
    #print(type(votes_over_time.index))
    return votes_over_time
    
def make_timeseries(votes_over_time):
    fig, ax = plt.subplots(
            figsize = (30, 9))
    fig.autofmt_xdate()
    width = (max(votes_over_time) - min(votes_over_time)) / len(votes_over_time) * 2.5
    ax.bar(
            votes_over_time.index, votes_over_time.values,
            color="#72CDFE",
            width=-width, align='edge')
    ax.set_title("Total votes over time")
    ax.set_xlabel("Month, Year")
    ax.set_ylabel("Votes")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%B, %Y'))
    ax.xaxis.set_major_locator( mdates.MonthLocator(interval=1))
    ax.tick_params(axis='x', rotation=80)
    return fig

def make_heatmap(heatmap, dates, places):
    x, y = np.meshgrid(places, dates)
    color_map = mcolors.LinearSegmentedColormap.from_list("custom_cmap", [tk_blue, tk_orange])
    
    fig, ax = plt.subplots(figsize = (9, 24))
    fig.autofmt_xdate()
    plot = ax.pcolormesh(x, y, heatmap, cmap=color_map, edgecolors='black', lw=0.1)

    ax.yaxis.set_major_formatter(mdates.DateFormatter('%B, %Y'))
    ax.yaxis.set_major_locator( mdates.MonthLocator(interval=3))
    ax.set_title("Number of votes per place over time")
    fig.colorbar(plot)

    return fig

def get_heatmap_data(df):
    max_place = 5
    slc_df = df.loc[:,['date','place', votes]]
    # Remove runner ups
    top_bool = slc_df['place'].astype(str).str.isdigit()
    slc_df = slc_df[top_bool] 
    # Remove ties/duplicates
    slc_df.drop_duplicates(inplace=True)
    # Imputate missing months

    uniq_dates = pd.unique(df['date'])
    heatmap_array = []
    placement = [0] * (max_place)
    curr_date = uniq_dates[0]
    for index,  row in slc_df.iterrows():
        place = row['place']
        count = row[votes]
        date = row['date']
        placement[place-1]=count
        if place == max_place:
        # if curr_date != date:
            print(placement, date, place)
            heatmap_array.append(placement)
            placement = [0] * max_place
            curr_date = date

    places = list(range(1, max_place+1))
    #     print(heatmap_array)
    np_heatmap = np.array(heatmap_array)
    return heatmap_array, uniq_dates, places


if __name__=="__main__":
    plt.style.use('seaborn-v0_8-darkgrid')
    args = proc_opts()
    twk_df = read_file(args.filename) 
    time_ser = group_timeseries(twk_df)

    heatmap, dates, places = get_heatmap_data(twk_df)
    heat_map_fig = make_heatmap(heatmap, dates, places)

    hist_fig = make_histogram(twk_df)
    time_fig = make_timeseries(time_ser)

    if args.dry_run:
        sys.exit(0)
    if args.graph_out:
        hist_fig.savefig(args.graph_out+"histogram.png")
        time_fig.savefig(args.graph_out+"timeseries.png")
        heat_map_fig.savefig(args.graph_out+"heatmap.png")
    else:
        plt.show()
