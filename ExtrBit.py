import os
import cv2
import numpy as np
from descripteur import bitdesc

def ExtractionSignatures(chemin_repertoire):
    list_carac = []
    for root, _, files in os.walk(chemin_repertoire):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                relative_path = os.path.relpath(os.path.join(root, file), chemin_repertoire)
                path = os.path.join(root, file)
                try:
                    carac = bitdesc(path)
                    class_name = os.path.dirname(relative_path)
                    carac = carac + [class_name, relative_path]
                    list_carac.append(carac)
                except:
                    pass
    signatures = np.array(list_carac)
    np.save('SignaturesBiT.npy', signatures)
    print("Signatures sauvegardées dans SignaturesBiT.npy")

def main():
    ExtractionSignatures('./dataset/')

if __name__ == '__main__':
    main()

