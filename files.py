import numpy as np
import h5py as h5

def datamerge(h5g, *items):
    items = list(items)
    i = 0
    dsets = list()
    size = 0
    while i < len(items):
        it = h5g[items[i]]
        if type(it) is h5.Dataset:
            dsets.append(it)
            size += len(it)
        else:
            for key in it.keys():
                items.append(items[i] + "/" + key)
        i += 1
    dta = np.zeros([size, 3])
    start = 0
    for dset in dsets:
        l = len(dset)
        dta[start:start+l,:] = dset
        start += l
    return dta

def dataread(f, *args):
    if type(args[len(args)-1]) is not list:
        args = (*args,[0, 9999])
    g = f
    for arg in range(0, len(args)-1):
        g = g[args[arg]]
    gr = list()
    lim = args[len(args)-1]
    for k in g.keys():
        if int(k) > lim[1]:
            break
        if int(k) >= lim[0]:
            gr.append(k)
    return datamerge(g, *gr)
