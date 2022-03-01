import os

import pandas as pd
import numpy as np

import warnings

warnings.simplefilter("ignore")

import seaborn as sns
import matplotlib.pyplot as plt


def readFREDdata():
    file = r"D:\0_Work\Pycharm\DS105-Data-Storage\FRED Data\FGCCSAQ027S.xls"

    data = pd.read_excel(file, sheet_name="FRED Graph")

    stop = False
    index = 0

    while not stop:
        value = data.at[index, data.columns[0]]

        if value != "observation_date":
            data.drop(labels=[index], inplace=True)
            index += 1
        else:
            data.drop(labels=[index], inplace=True)
            stop = True

    data.reset_index(drop=True, inplace=True)
    data.rename(mapper={data.columns[0]: "Observation", data.columns[1]: "Student Loans in Millions"},
                inplace=True, axis=1)

    print(data.head())


def readKaggleDatasets():
    keyAttributes = ["INSTNM", "STABBR", "ADM_RATE", "TUITIONFEE_IN", "TUITIONFEE_OUT", "CDR3", "DEBT_MDN",
                     "GRAD_DEBT_MDN", "CUML_DEBT_N", "faminc", "DEBT_MDN_SUPP", "RPY_1YR_RT"]

    overall = {}
    for attr in keyAttributes:
        overall[attr] = []

    overall["Year"] = []

    folder = r"D:\0_Work\Pycharm\DS105-Data-Storage\Kaggle Datasets\datasets"
    year = 1996
    for file in os.listdir(folder):
        path = folder + "\\" + file

        data = pd.read_csv(path)

        for key in keyAttributes:
            overall[key] += list(data[key])

        for i in range(data.shape[0]):
            overall["Year"].append(year)

        year += 1

    overall = pd.DataFrame.from_dict(overall)

    overall.to_csv(path_or_buf="test.csv")


def plotAttributeTimeSeries(attr, name):
    data = pd.read_csv("test.csv")

    years = pd.unique(data["Year"])
    states = pd.unique(data["STABBR"])

    filtered = pd.DataFrame()

    for i in range(len(years)):
        year = years[i]
        filtered.at[i, "Year"] = year
        for state in states:
            sub = data[(data["Year"] == year) & (data["STABBR"] == state)][attr]
            sub.dropna(inplace=True)

            avg = np.average(sub)

            filtered.at[i, state] = avg

    filtered = filtered[filtered.columns[0:10]]

    sns.set(rc={"figure.figsize": (11.7, 8.27)})

    setup = pd.melt(filtered, "Year", value_name=name)
    ax = sns.lineplot(x="Year", y=name, hue="variable", data=setup)
    sns.move_legend(ax, loc="upper left", title="State", bbox_to_anchor=(1, 1))
    ax.set_title(name + " over time")

    plt.show()



plotAttributeTimeSeries("TUITIONFEE_IN", "In-state Tuition")
