import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy.stats import pearsonr 
import scipy.stats as stats



def upper_shadow(df): 
    return df['High'] - np.maximum(df['Close'], df['Open'])

def lower_shadow(df): 
    return np.minimum(df['Close'], df['Open']) - df['Low']

def get_features(df, row = False)->pd.DataFrame:
    """Finanz Indikatoren
        https://www.kaggle.com/code/swaralipibose/lgdm-model-with-new-features-better-generalization/
    Args:
        df : aktulles Dataframe
        row (bool, optional): Defaults to False.
        

    Returns:
        pd.DataFrame: Ursprüngliches Dataframe mit Indikatoren
    """
    df_feat = df
    df_feat['mean_trade'] = df_feat['Volume']/df_feat['Count']
    df_feat['upper_Shadow'] = upper_shadow(df_feat)
    df_feat['lower_Shadow'] = lower_shadow(df_feat)
    df_feat['shadow3'] = df_feat['upper_Shadow'] / df_feat['Volume']
    df_feat['shadow5'] = df_feat['lower_Shadow'] / df_feat['Volume']
    df_feat['mean1'] = (df_feat['shadow5'] + df_feat['shadow3']) / 2
    df_feat['UPS'] = (df_feat['High'] - np.maximum(df_feat['Close'], df_feat['Open']))
    df_feat['LOS'] = (np.minimum(df_feat['Close'], df_feat['Open']) - df_feat['Low'])
    df_feat['LOGVOL'] = np.log(1. + df_feat['Volume'])
    df_feat['LOGCNT'] = np.log(1. + df_feat['Count'])
    if row: df_feat['Mean'] = df_feat[['Open', 'High', 'Low', 'Close']].mean()
    else: df_feat['Mean'] = df_feat[['Open', 'High', 'Low', 'Close']].mean(axis = 1)
    df_feat["High/Mean"] = df_feat["High"] / df_feat["Mean"]
    df_feat["Low/Mean"] = df_feat["Low"] / df_feat["Mean"]
    df_feat["Volume/Count"] = df_feat["Volume"] / (df_feat["Count"] + 1)
    mean_price = df_feat[['Open', 'High', 'Low', 'Close']].mean(axis=1)
    df_feat['high2mean'] = df_feat['High'] / mean_price
    df_feat['low2mean'] = df_feat['Low'] / mean_price
    df_feat['volume2count'] = df_feat['Volume'] / (df_feat['Count'] + 1)
    print(df_feat)
    return df_feat



def decomposition_noise(df:pd.DataFrame,period=60)->pd.DataFrame:
    """Calc Dekomposition, Mult, Periode default 60, add noise to DF

    Args:
        df (pd.DataFrame): Ursprungs Dataframe 
        period (int, optional): Periode. Defaults to 60.

    Returns:
        pd.DataFrame: Urpsprüngliches Dataframe mit Noise-Multi-Dekomposition
    """
    df_feat = df
    result_mult=seasonal_decompose(df_feat['Close'], model='multiplicative', period=period)
    df_feat["noise_mult"] = result_mult.resid
    return df_feat

def fft_feature(df:pd.DataFrame)->pd.DataFrame:
    """FFT als Feature in den Schritten 5, 15, 50

    Args:
        df (pd.DataFrame): Ursprungs Dataframe

    Returns:
        pd.Dataframe: Ursprungs Dataframe mit neuen FFT Features
    """
    df_feat = df
    close_fft = np.fft.fft(np.asarray(df_feat['Close'].tolist()))
    fft_df = pd.DataFrame({'fft':close_fft})
    fft_df['absolute'] = fft_df['fft'].apply(lambda x: np.abs(x))
    fft_df['angle'] = fft_df['fft'].apply(lambda x: np.angle(x))
    fft_list = np.asarray(fft_df['fft'].tolist())
    for num_ in [5, 15, 50]:
        fft_list= np.copy(fft_list); fft_list[num_:-num_]=0
        df_feat["fft_" + str(num_)] = np.fft.ifft(fft_list).real
    return df_feat
    

def tech_analysis(df:pd.DataFrame) -> pd.DataFrame:
    """Moving Average Indiaktor 

    Args:
        df (pd.DataFrame): Ursprungs Dataframe

    Returns:
        pd.DataFrame: Ursprungs Dataframe mit neuen MA Features
    """
    df_feat = df
    df_feat["MA_20"] = df_feat["Close"].rolling(20).mean()
    df_feat["MA_diff"] = np.log(1+(df_feat.MA_20 - df_feat.Close)/df_feat.Close.shift(1))
    return df_feat
    
def get_macd(price, slow, fast, smooth):
    """MACD - not used

    Args:
        price (float): preis
        slow (float): slow macd
        fast (float): fast macd
        smooth (float): smooth macd

    Returns:
        pd.DataFrame: Ursprungs Dataframe mit neuen MACD Features
    """
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'Close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
    frames =  [macd, signal, hist]
    df = pd.concat(frames, join = 'inner', axis = 1)
    return df

def outlier_correction(df):
    df_feat = df
    df_feat = np.log(1+(df_feat["Close"]-df_feat["Close"].shift(1))/df_feat["Close"].shift(1))
    df_feat = detect_outliers(df_feat)
    
    
#https://github.com/krishnaik06/Finding-an-Outlier/blob/master/Finding%20an%20outlier%20in%20a%20Dataset.ipynb
def detect_outliers(data,std_threshold=15): 
    """Ausreißer Erkennung und Korrektur

    Args:
        data (pd.DatamFrame): Ursprungs DataFrame
        std_threshold (int, optional): Z-Score Standardabweichung ab der korrigiert werden soll. Defaults to 15.

    Returns:
        pd.DataFrame: DataFrame mit korrigierte Verteilung
    """
    row_names = ["High","Open","Low","Close"]
    df = data
    for column in row_names:
        log_column_name = "Log_" + column
        df[log_column_name] = np.log(1+(df[column]-df[column].shift(1))/df[column].shift(1))
    df = df.iloc[1: , :]
    threshold=std_threshold
    mean = np.mean(df["Log_Close"])
    std =np.std(df["Log_Close"])
    df["zscores"] = stats.zscore(df["Log_Close"])
    counter = 0
    for index, row in df.iterrows():
            if row["zscores"] > threshold:
                data.at[index, "Log_Close"] = (threshold*std)+mean
                counter += 1
            elif row["zscores"] < threshold*-1:
                data.at[index, "Log_Close"] = (-1*threshold*std)+mean
                counter += 1
    df["Log_Close"] = df["zscores"]
    return df

def feature_seasonal(df:pd.DataFrame)->pd.DataFrame:
    """Ergänzung saisonale Features

    Args:
        df (pd.DataFrame): Ursprungs Dataframe

    Returns:
        pd.DataFrame: Dataframe mit saisonalen Features
    """
    df_feat = df
    df_feat["Minute"] = df_feat.index.minute
    df_feat["Day"] = df_feat.index.day
    df_feat["Month"] = df_feat.index.month
    df_feat["Year"] = df_feat.index.year
    df_feat["DayOfWeek"] = df_feat.index.dayofweek
    season_log = df_feat["Log_Close"]
    seasonal_min =  season_log.groupby(season_log.index.minute).median()
    df_feat["minute_seasonal"] = df_feat.Minute.apply(min_mapper, pd_series = seasonal_min)
    def get_correlation(vals):
        return pearsonr(vals, seasonal_min)[0]
    df_feat['correlation_log_perf'] = season_log.rolling(window=len(seasonal_min)).apply(get_correlation)
    return df_feat
    


def min_mapper(value,pd_series):
    return pd_series.loc[value]


def createFeature(df):
    """Erstellt teil der Features

    Args:
        df (pd.DataFrame): Ursprungs Dataframe

    Returns:
        pd.DataFrame : Alle Features im DF
    """
    df_1 = get_features(df)
    print("Step 1")
    df_2 = decomposition_noise(df_1)
    print("Step 2")
    df_3 = fft_feature(df_2)
    print("Step 3")
    df_4 = tech_analysis(df_3)
    print("Step 4")
    df_4 = df_4.dropna()
    return df_4
    
    


def featuresGen(data:pd.DataFrame)->pd.DataFrame:
    """Hauptfunktion für die Generiung der Feeatures

    Args:
        data (pd.DataFrame): Urpsrungs Dataframe

    Returns:
        pd.DataFrame: Dataframe mit allen Features
    """
    data = createFeature(data)
    data = data.dropna()
    data = detect_outliers(data)
    data = feature_seasonal(data)
    data = data.dropna()
    data_label = []
    for index,value in data["Target"].items():
        if value < 0:
            data_label.append(1)
        elif value > 0:
            data_label.append(0)
        else:
            data_label.append(0)
    data["Label"] = data_label
    return data