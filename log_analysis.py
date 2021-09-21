#!/usr/bin/env python3
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from plotly.subplots import make_subplots

if __name__ == '__main__':
    files = list(Path('logs').rglob('esp-module*.log'))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for file in files:
        df = pd.read_csv(file, header=None)
        values = df[(df[1] > 55) | (df[1] < 52)]
        # print(values)
        # print(list(df))
        # print(list(df.index.values))
        # fig.add_trace(go.Scatter(x=df.index.values, y=df[0], name=f'{file} time'), secondary_y=False)
        fig.add_trace(go.Scatter(x=values.index.values, y=values[1], name=f'{file} diff'), secondary_y=True)
    fig.update_yaxes(secondary_y=True)
    fig.show()
