import os

import pandas as pd
import numpy as np

import warnings

warnings.simplefilter("ignore")

import seaborn as sns
import matplotlib.pyplot as plt

from collections import Counter

states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
          'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
          'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
          'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
          'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']


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


def readKaggleDatasets(keyAttributes):
    keyAttributes.append("STABBR")
    keyAttributes.append("INSTNM")
    overall = {}
    for attr in keyAttributes:
        overall[attr] = []

    overall["Year"] = []

    folder = r"D:\0_Work\Python Projects\DS105-Data-Storage\Kaggle Datasets\datasets"
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
    overall = overall[overall["STABBR"].isin(states)]


    return overall


def getSchoolCounts():
    data = pd.read_csv("test.csv")
    data = data[data["Year"] == 2013]
    counts = Counter(data["STABBR"])
    counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    return list(counts.keys())


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

    schools = getSchoolCounts()[:11]
    schools.append("Year")

    filtered = filtered[schools]

    sns.set(rc={"figure.figsize": (11.7, 8.27)})

    setup = pd.melt(filtered, "Year", value_name=name)
    ax = sns.lineplot(x="Year", y=name, hue="variable", data=setup)
    sns.move_legend(ax, loc="upper left", title="State", bbox_to_anchor=(1, 1))
    ax.set_title(name + " over time")

    plt.show()


def barChartCollegeScorecardData(attr, name, year):
    data = pd.read_csv("test.csv")

    filtered = data[data["Year"] == year][["STABBR", attr]]
    states = list(pd.unique(filtered["STABBR"]))
    states = sorted(states)

    averages = pd.DataFrame()
    for i in range(len(states)):
        state = states[i]

        sub = filtered[filtered["STABBR"] == state]
        sub.dropna(inplace=True)

        avg = np.average(sub[attr])
        averages.at[i, "State"] = state
        averages.at[i, name] = avg

    sns.barplot(x="State", y=name, data=averages).set_title(f"{name} in {year} by State")
    plt.show()


def transformAttrsToStateLevel(attrs, name, year):
    data = readKaggleDatasets(attrs)
    data = data[data["Year"] == year]
    saveVal = pd.DataFrame()
    index = 0

    for state in states:
        sub = data[data["STABBR"] == state]

        saveVal.at[index, "State"] = state

        for attr in attrs:
            points = list(sub[attr].dropna())
            avg = np.average(points)
            saveVal.at[index, attr] = avg

        index += 1

    xlw = pd.ExcelWriter("Visualization Datasets\\" + name + ".xlsx")
    saveVal.to_excel(xlw, sheet_name="main", index=False)
    xlw.save()


def boxPlotBlackInst():
    data = readKaggleDatasets(["UGDS_BLACK", "DEBT_MDN", "mn_earn_wne_p6"])
    data = data[data["Year"] == 2011]
    data.replace("PrivacySuppressed", None, inplace=True)
    data.dropna(inplace=True)
    data.reset_index(inplace=True, drop=True)

    sns.boxplot(data=data, x="UGDS_BLACK")
    plt.show()

    desc = data["UGDS_BLACK"].describe()

    quartiles = [desc["25%"], desc["50%"], desc["75%"]]
    for i in range(data.shape[0]):
        val = data.at[i, "UGDS_BLACK"]

        quartSet = False
        for a in range(len(quartiles)):
            bench = quartiles[a]
            if val <= bench:
                data.at[i, "Quartile"] = a + 1
                quartSet = True
                break

        if not quartSet:
            data.at[i, "Quartile"] = 4

    data[["DEBT_MDN", "mn_earn_wne_p6"]] = data[["DEBT_MDN", "mn_earn_wne_p6"]].astype(float)

    sns.relplot(data=data, x="DEBT_MDN", y="mn_earn_wne_p6", col="Quartile")
    plt.show()


def main():
    used_attributes = ["PBI", "CDR3", "TUITIONFEE_IN", "TUITIONFEE_OUT", "C150_4_WHITE", "C150_4_BLACK", "C150_4_HISP",
                       "C150_4_ASIAN", "C150_4_NHPI", "C150_4_2MOR", "C150_4_NRA", "C150_4_UNKN",
                       "UGDS_WHITE", "UGDS_BLACK", "UGDS_HISP", "UGDS_ASIAN"]


def countInstOverTime():
    data = readKaggleDatasets(["PBI"])

    years = list(data["Year"].unique())

    saveVal = pd.DataFrame()

    for state in states:
        for year in years:
            sub = data[(data["STABBR"] == state) & (data["Year"] == year)]
            institutions = len(sub["INSTNM"])

            saveVal.at[state, year] = institutions

    saveVal.to_excel("Visualization Datasets\\instiution count data.xlsx")


countInstOverTime()