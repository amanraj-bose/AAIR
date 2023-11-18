import numpy as np
from collections import Counter

def ensemble(x, model, term=5, n=2):
    gender = []
    ethnicity = []
    for _ in range(term):
        X = model(x, training=False)
        gender.append(np.asarray(X[0] > .5).tolist()[-1][-1])
        ethnicity.append(
            np.argmax(X[1].numpy())
        )
    
    ethnicity = Counter(ethnicity)
    gender = Counter(gender)
    try:
        ethnicity = [ethnicity.most_common()[0][0], ethnicity.most_common()[0][1]]
    except IndexError:
        ethnicity = [ethnicity.most_common()[0][0]]

    return gender.most_common()[0][0], ethnicity

