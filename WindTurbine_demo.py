import WindTurbine as wt
# Initiate the instance
edata = wt.EnerconWindTurbineData()
edata.import_data()
edata.clean_data()
edata.create_new_features()
edata.create_lagged_features(6)
edata.create_mean_std_features()
edata.derived_features = pd.concat([edata.new_features, edata.lagged_features, edata.mean_std], axis=1, join='inner')
# To save memory, delete the redundant dataframes
edata.derived_features.dropna(inplace=True)
edata.xdata = pd.concat([edata.derived_features, edata.scada_data], axis=1, join='inner')
edata.xdata.to_pickle('xdata_all_unscaled.p')