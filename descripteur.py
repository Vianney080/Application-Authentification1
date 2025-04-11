from skimage.feature import graycomatrix, graycoprops
from mahotas.features import haralick
from BiT import bio_taxo
import cv2
import numpy as np

def glcm(chemin):
    data=cv2.imread(chemin,0)
    co_matrice=graycomatrix(data,[1],[np.pi/2],None,symmetric=True,normed=False)
    contrast=float(graycoprops(co_matrice,'contrast')[0,0])
    dissimilarity=float(graycoprops(co_matrice,'dissimilarity')[0,0])
    homogeneity=float(graycoprops(co_matrice,'homogeneity')[0,0])
    correlation=float(graycoprops(co_matrice,'correlation')[0,0])
    ASM=float(graycoprops(co_matrice,'ASM')[0,0])
    energy=float(graycoprops(co_matrice,'energy')[0,0])
    return [contrast,dissimilarity,homogeneity,correlation,ASM,energy]

def haralick_feat(chemin):
    data = cv2.imread(chemin, 0)
    features = haralick(data).mean(0).tolist()
    return [float(x) for x in features]

def bitdesc(chemin):
    data = cv2.imread(chemin, 0)
    features = bio_taxo(data)
    return [float(x) for x in features]

def concatenation(chemin):
    return glcm(chemin) + haralick_feat(chemin) + bitdesc(chemin)
