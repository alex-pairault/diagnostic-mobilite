import numpy as np

from sklearn.preprocessing import OneHotEncoder

from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler


def find_distances(to_match, sources, n_neighbors=10):
    sources["pond_indC"] = sources["pond_indC"].astype("float64")

    std_X, std_samples = prepare_data_for_nneighbors(to_match, sources)
    n_neighbors_index = find_nneighbors(std_X, std_samples, n_neighbors)
    matched_indexes = nneighbors_indexes_to_index(n_neighbors_index, sources)

    distances = sources.iloc[matched_indexes]["__work_dist"].tolist()
    modes = sources.iloc[matched_indexes]["__work_transport"].tolist()
    return distances, modes


def prepare_data_for_nneighbors(to_match, sources):
    to_match["__work_transport"] = to_match["__work_transport"].fillna("Z")
    sources["__work_transport"] = sources["__work_transport"].fillna("Z")

    cat_attr = ["SEXE", "__csp", "STATUTCOM_UU_RES"]
    quant_attr = ["AGE", "NPERS", "NENFANTS", "JNBVEH"]

    print(to_match)
    print(sources)
    print(to_match.dtypes)
    print(sources.dtypes)

    # prepare data
    min_max_scaler = MinMaxScaler()
    one_hot = OneHotEncoder()

    # print("-- standardize sources = samples")
    print(sources.loc[sources.loc[:, quant_attr].isna().any(axis=1), quant_attr])
    sources_quant = sources.loc[:, quant_attr].fillna(1000).astype("int32")
    print(sources_quant)
    std_sources_quant = sources_quant.to_numpy()
    print(std_sources_quant)
    minmax_sources_quant = min_max_scaler.fit_transform(std_sources_quant)

    sources_cat = sources.loc[:, cat_attr]
    print(sources_cat)
    onehot_sources_cat = one_hot.fit_transform(sources_cat.to_numpy()).toarray()
    print(onehot_sources_cat)

    std_samples = np.concatenate((minmax_sources_quant, onehot_sources_cat), axis=1)

    # print("-- standardize persons to match")
    print(to_match.loc[to_match.loc[:, quant_attr].isna().any(axis=1), quant_attr])
    to_match_quant = to_match.loc[:, quant_attr].fillna(1000).astype("int32")
    print(to_match_quant)
    std_to_match_quant = to_match_quant.to_numpy()
    print(std_to_match_quant)
    minmax_to_match_quant = min_max_scaler.transform(std_to_match_quant)

    to_match_cat = to_match.loc[:, cat_attr]
    print(to_match_cat)
    onehot_to_match_cat = one_hot.transform(to_match_cat.to_numpy()).toarray()
    print(onehot_to_match_cat)

    std_X = np.concatenate((minmax_to_match_quant, onehot_to_match_cat), axis=1)
    return std_X, std_samples


def find_nneighbors(std_X, std_samples, nneighbors):
    # print("-- compute nearest neighbors")
    neigh = NearestNeighbors(n_neighbors=nneighbors, radius=0.1, metric="manhattan")
    neigh.fit(std_samples)

    print("-- find nearest neighbors")
    r_neighbors_dist, r_neighbors_index = neigh.radius_neighbors(std_X, return_distance=True)
    n_neighbors_dist, n_neighbors_index = neigh.kneighbors(std_X, return_distance=True)

    neighbors_index = [ri if len(ri) >= nneighbors else ni for ri, ni in zip(r_neighbors_index, n_neighbors_index)]

    neighbors_dist = np.array([[np.mean(rd)] * nneighbors if len(rd) >= nneighbors else nd for rd, nd in
                               zip(r_neighbors_dist, n_neighbors_dist)])
    neighbors_r_n = [True if len(ri) >= nneighbors else False for ri, ni in
                     zip(r_neighbors_index, n_neighbors_index)]
    print(f"Proportion de radius neighbors : {round(sum(neighbors_r_n) / len(neighbors_r_n) * 100)}%")
    print(f"Distances - part > 0 {(np.sum(neighbors_dist > 0, axis=0) / len(neighbors_dist) * 100).round(2)}")
    print(f"Distances - part >= 2 {(np.sum(neighbors_dist >= 2, axis=0) / len(neighbors_dist) * 100).round(2)}")
    print(f"Distances - part >= 4 {(np.sum(neighbors_dist >= 4, axis=0) / len(neighbors_dist) * 100).round(2)}")
    print(f"Distances - part >= 6 {(np.sum(neighbors_dist >= 6, axis=0) / len(neighbors_dist) * 100).round(2)}")
    print(f"Moyenne des distances {np.mean(neighbors_dist, axis=0)}")
    print(f"Médiane des distances {np.median(neighbors_dist, axis=0)}")
    print(f"Moyenne : {np.mean(neighbors_dist)}")
    print(f"Variance : {np.var(neighbors_dist)}")
    return neighbors_index


def nneighbors_indexes_to_index(n_neighbors_index, sources):
    def indexes_to_index(indexes):
        weights = sources.iloc[indexes]["pond_indC"]
        ind = np.random.choice(indexes, p=weights/weights.sum())
        return ind

    matched_indexes = [indexes_to_index(indexes) for indexes in n_neighbors_index]
    return matched_indexes