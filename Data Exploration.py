import os
import pandas as pd


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



readKaggleDatasets()