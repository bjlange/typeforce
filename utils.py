import matplotlib.pyplot as plt


def test_fit(series, dist):    
    thinkplot.Cdf(ts2.Cdf(series))
    plt.plot(np.linspace(series.min(),series.max(),100), 
             dist(*dist.fit(series)).cdf(np.linspace(series.min(),series.max(),100)))