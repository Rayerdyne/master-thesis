import numpy as np

from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import BaggingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error

from xgboost import XGBRegressor

from config import DATASET_PATH, TRAIN_SET_RATIO, TEST_SET_RATIO, VALIDATION_SET_RATIO
from train import fetch_data

def main():
    print("==== Loading data ====")
    x_train, y_train, x_test, y_test, x_val, y_val, normalizers = fetch_data(DATASET_PATH, TRAIN_SET_RATIO, TEST_SET_RATIO, VALIDATION_SET_RATIO)

    for n_neigh in range(4, 30):
        knn = KNeighborsRegressor(n_neighbors=n_neigh)

        knn.fit(x_train, y_train)
        y_pred = knn.predict(x_test)
        mseloss = mean_squared_error(y_test, y_pred)
        print("mse loss for", n_neigh, "neighbors: ", mseloss)
    
    for n_trees in range(25, 150, 10):
        extratrees = RandomForestRegressor(n_trees)

        extratrees.fit(x_train, y_train)
        y_pred = extratrees.predict(x_test)
        mseloss = mean_squared_error(y_test, y_pred)
        print("mse loss for", n_trees, "trees: ", mseloss)
    
    # for max_depth in [3, 4, 5, 6]:
    #     for lr in [0.1, 0.2, 0.3, 0.4]:
    #         for n in range(7, 15):
    #             xgb = XGBRegressor(
    #                 n_estimators=n,
    #                 learning_rate=lr,
    #                 max_depth=max_depth,
    #                 objective="reg:squarederror"
    #             )

    #             xgb.fit(x_train, y_train)
    #             y_pred = xgb.predict(x_test)
    #             mseloss = mean_squared_error(y_test, y_pred)
    #             print(f"XGBoost with lr {lr}, max depth {max_depth} and {n} estimators: {mseloss}")

    
    # for i in range(2, 20, 2):
    #     truca = BaggingRegressor(estimator=SVR(), n_estimators=i)
    #     truca.fit(x_train, y_train[:,0])
    #     trucb = BaggingRegressor(estimator=SVR(), n_estimators=i)
    #     trucb.fit(x_train, y_train[:,1])

    #     y_pred = np.column_stack([truca.predict(x_test), trucb.predict(x_test)])
    #     print("ypred", y_pred.shape, "t_test", y_test.shape)
    #     mseloss = mean_squared_error(y_test, y_pred)
    #     print("mse loss for", i, "svrs: ", mseloss)
    
    # mlpr = MLPRegressor([150, 100], learning_rate="adaptive")
    # mlpr.fit(x_train, y_train)
    # y_pred = mlpr.predict(x_test)
    # mseloss = mean_squared_error(y_test, y_pred)
    # print("mse loss mlpr: ", mseloss)

if __name__ == "__main__":
    main()