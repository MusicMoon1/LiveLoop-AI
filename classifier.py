import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder


# labels: chords
# inputs: midi notes
# problem: inputs are variable length
# solution: find longest vector, append shorter vectors with -1


def load_data():
    df = pd.read_csv("chords_extended.csv")

    df['midi_numbers'] = df['midi_numbers'].apply(lambda x: list(map(int, x.split(', '))))
    max_len = df['midi_numbers'].apply(len).max()

    midi_numbers_new = []
    for midi_num in df['midi_numbers']:
        while len(midi_num) < max_len:
            midi_num.append(-1)
        midi_numbers_new.append(midi_num)
    midi_numbers_new = midi_numbers_new[:384]
    midi_numbers_new = np.array(midi_numbers_new)

    chords = df["chord"][:384]
    chords = np.tile(chords, int(len(midi_numbers_new) / len(chords)))  # repeats entries in chords, matching the entries in midi_numbers_new

    return midi_numbers_new, chords



def classify(data, labels):
    # Encode string labels to integers
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(labels)

    best_score = 0
    best_model = None
    for i in range(2, 33):
        neigh = KNeighborsClassifier(n_neighbors=i, n_jobs=4)
        neigh.fit(data, y_encoded)
        score_t = neigh.score(data, y_encoded)

        if best_score < score_t:
            best_score = score_t
            best_model = neigh
        print(f"i: {i}, score: {score_t}, best_model: {best_model.get_params()['n_neighbors']}")
        
    return best_model, y_encoded



def plot(knn, X, y, labels):
    # Reduce dimensionality to 2D using PCA
    pca = PCA(n_components=2)
    X_reduced = pca.fit_transform(X)

    # Create color maps
    cmap_light = ListedColormap(['#FFAAAA', '#AAAAFF', '#AAFFAA', '#FFAAFF', '#AFFFFF', '#FFFFAA', '#FFAF55', '#55FFAF', '#AF55FF', '#FF55AF', '#55AFF5', '#F5FF55',
                                '#FFAACC', '#AACCAA', '#CCAACC', '#CCAAFF', '#AACCFF', '#FFCCAA', '#AAFFCC', '#CCAA00', '#00AAFF', '#AACC55', '#55AACC', '#FFAA00',
                                '#CC55AA', '#FF55FF', '#AA00FF', '#FF0055', '#00FF55', '#55AA55', '#AAFF00', '#FFAA55'])
    cmap_bold = ListedColormap(['#FF0000', '#0000FF', '#00FF00', '#FF00FF', '#00FFFF', '#FFFF00', '#FFAA00', '#00FFAA', '#AA00FF', '#FF00AA', '#00AAFF', '#AAFF00',
                                '#FF5555', '#5555FF', '#55FF55', '#FF55FF', '#55FFFF', '#FFFF55', '#FFAA55', '#55FFAA', '#AA55FF', '#FF55AA', '#55AAFF', '#AAFF55',
                                '#FF5555', '#55FF55', '#FF5555', '#5555FF', '#55FFFF', '#FFFF55', '#FFAA55', '#55FFAA'])

    # Plot decision boundaries on reduced data
    print("Plotting decision boundaries")
    h = .5  # step size in the mesh, standard 0.02 (increasing lowers resolution)
    x_min, x_max = X_reduced[:, 0].min() - 1, X_reduced[:, 0].max() + 1
    y_min, y_max = X_reduced[:, 1].min() - 1, X_reduced[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))
    
    # Predict on the grid points, first transforming to original feature space
    print("Transforming to original feature space")
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    grid_points_original_space = pca.inverse_transform(grid_points)
    print("Predicting on grid points")
    Z = knn.predict(grid_points_original_space)

    # Debugging steps to inspect Z
    print(f"Z shape: {Z.shape}")
    print(f"Z data type: {Z.dtype}")
    print(f"Unique values in Z: {np.unique(Z)}")  # these should be the labels as integers

    # Put result into a color plot
    print("Putting result into color plot")
    Z = Z.reshape(xx.shape)
    plt.figure(figsize=(8, 6))
    plt.contourf(xx, yy, Z, cmap=cmap_light)

    # Select a subset of data points to plot
    subset_size = 250
    indices = np.random.choice(range(X_reduced.shape[0]), size=subset_size, replace=False)
    X = X_reduced[indices]
    y = y[indices]

    # Plot training points
    print("Plotting")
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_bold, edgecolor='k', s=20)
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.title(f"32-class classification - neighbors: {knn.get_params()['n_neighbors']}")
    plt.xlabel('PC 1')
    plt.ylabel('PC 2')

    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=cmap_bold(i), markersize=8, label=labels[i]) for i in range(len(labels))]
    plt.legend(handles=handles, title="Classes", bbox_to_anchor=(1, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig('knn_classification.png')
    plt.show()



if __name__ == "__main__":
    data, labels = load_data()
    best_model, y_encoded = classify(data, labels)
    plot(best_model, data, y_encoded, labels)
