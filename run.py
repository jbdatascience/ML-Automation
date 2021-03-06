import time
import json
import numpy as np

from load_data import load_data
from auto_ml import auto_ml

from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor

# Files
files = []
for sim in np.arange(1, 11):

    files.append({"train": "../data/Xy/" + str(sim) + "_train.csv",
                  "test": "../data/Xy/" + str(sim) + "_test.csv",
                  "task": "regression",
                  "name": str(sim)})

# Backends
backends = ["sklearn", "h2o", "tpot"]

# Settings
runs = 10  # number of random data sets
time_to_run = 60  # run time for each dataset and engine in minutes
folds = 5  # number of folds used in cv

# Loop over datasets
#for run in [8, 9, ]:
for run in np.arange(runs):

    # Load/Sim data
    X_train, y_train, X_test, y_test = load_data(path_train=files[run]["train"], path_test=files[run]["test"])

    # Random Forest Benchmark
    print("Fitting Benchmark via Random Forest")
    mod_rf = RandomForestRegressor(n_estimators=250)
    mod_rf.fit(X=X_train, y=y_train)
    y_hat_rf = mod_rf.predict(X=X_test)
    mse_benchmark = mean_squared_error(y_true=y_test, y_pred=y_hat_rf)

    # Loop over backends
    for engine in backends:

        # Verbose
        print("Starting ", engine + " in " + str(run), "run")

        # Start time tracking
        start_time = time.time()

        try:

            # Init model
            mod = auto_ml(backend=engine)
            mod.create_ml(run_time=time_to_run, folds=folds)

            # Fitting on training set
            mod.fit(X=X_train, y=y_train)

            # Predict on test set
            y_hat = mod.predict(X=X_test)

            # End time tracking
            time_elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))

            # Eval error on test set
            mse_score = mean_squared_error(y_true=y_test, y_pred=y_hat)

            # Results
            info = {"run": int(run),
                    "backend": engine,
                    "mse_test": mse_score,
                    "mse_benchmark": mse_benchmark,
                    "time_elapsed": time_elapsed}

            # Write log
            with open("../results/" + time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime(time.time())) + "_" + str(run) + "_" + str(engine) + ".json", "w") as outfile:
                json.dump(info, outfile, sort_keys=True, indent=4)

            # Verbose
            print("Finished " + engine + " in " + str(run) + " run")

        except (RuntimeError, TypeError, NameError):
            print("Error in " + "backend " + engine + " for " + str(run), "run")




