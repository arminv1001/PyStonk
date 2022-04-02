import pandas as pd
def run_strategy(master_df)->pd.DataFrame:
    data_path = r"C:\\Users\\Armin\\Documents\\Code\\Studienarbeit\\crypto_daten_kaggle\\"
    crypto_df = pd.read_hdf("train.h5")
    for i in range(0,14):
        print(i)
        btc = crypto_df[crypto_df["Asset_ID"]==i]
        btc["timestamp"] = pd.to_datetime(btc["timestamp"], unit='s')
        btc.set_index("timestamp",inplace=True)

        btc = createFeature(btc)
        btc = btc.dropna()
        btc = detect_outliers(btc)
        btc = feature_seasonal(btc)
        btc = btc.dropna()
        btc_target_label = []
        for index,value in btc["Target"].items():
            if value < 0:
                btc_target_label.append(1)
            elif value > 0:
                btc_target_label.append(0)
            else:
                btc_target_label.append(0)
        btc["Label"] = np.array(btc_target_label)
        btc = btc.drop(["Target","Asset_ID","index","Open","High","Low","Close"], axis=1).reset_index(drop=True)
        btc.to_hdf('Data/' + str(i) + '_V1.h5', key='df', mode='w')