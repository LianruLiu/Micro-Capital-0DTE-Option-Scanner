import numpy as np
from scipy.stats import norm

def black_scholes_call(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)

    call = S * norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)

    delta = norm.cdf(d1)
    gamma = norm.pdf(d1) / (S*sigma*np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100

    return call, delta, gamma, vega


S = 100
K = 100
T = 30/365
r = 0.03
sigma = 0.25

call, delta, gamma, vega = black_scholes_call(S,K,T,r,sigma)

print("Call Price:", round(call,4))
print("Delta:", round(delta,4))
print("Gamma:", round(gamma,4))
print("Vega:", round(vega,4))