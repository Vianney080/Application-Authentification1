
import numpy as np
from scipy.spatial import distance

def manhattan(v1, v2):
    v1 = np.array(v1).astype('float')
    v2 = np.array(v2).astype('float')
    return np.sum(np.abs(v1 - v2))

def euclidienne(v1, v2):
    v1 = np.array(v1).astype('float')
    v2 = np.array(v2).astype('float')
    return np.sqrt(np.sum((v1 - v2)**2))

def chebyshev(v1, v2):
    v1 = np.array(v1).astype('float')
    v2 = np.array(v2).astype('float')
    return np.max(np.abs(v1 - v2))

def canberra(v1, v2):
    v1 = [float(i) for i in v1]
    v2 = [float(i) for i in v2]
    return distance.canberra(v1, v2)

def RechercheImage(siganturebase, carac_img_requete, distances, K):
    list_similaire = []
    for instance in siganturebase:
        carac, label, img_chemin = instance[:-2], instance[-2], instance[-1]

        if distances == 'canberra':
            dist = canberra(carac, carac_img_requete)
        elif distances == 'euclidienne':
            dist = euclidienne(carac, carac_img_requete)
        elif distances == 'chebyshev':
            dist = chebyshev(carac, carac_img_requete)
        elif distances == 'manhattan':
            dist = manhattan(carac, carac_img_requete)
        else:
            raise ValueError("Distance inconnue")

        list_similaire.append((img_chemin, dist, label))

    list_similaire.sort(key=lambda x: x[1])
    return list_similaire[:K]
