import pandas as pd
import argparse
import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import sys

votes='number of votes'
name='sketch names'
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


if __name__=="__main__":
    plt.style.use('seaborn-v0_8-darkgrid')
    args = proc_opts()
    twk_df = read_file(args.filename) 

    hist_fig = make_histogram(twk_df)
    time_fig = group_timeseries(twk_df)

    if args.dry_run:
        sys.exit(0)
    if args.graph_out:
        hist_fig.savefig(args.graph_out+"histogram.png")
        time_fig.savefig(args.graph_out+"timeseries.png")
    else:
        plt.show()
