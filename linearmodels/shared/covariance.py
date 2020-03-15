import numpy as np
from numpy import argsort, r_, unique, where, zeros

from linearmodels.typing import NDArray


def group_debias_coefficient(clusters: NDArray) -> float:
    r"""
    Compute the group debiasing scale.

    Parameters
    ----------
    clusters : ndarray
        One-dimensional array containing cluster group membership.

    Returns
    -------
    float
        The scale to debias.

    Notes
    -----
    The debiasing coefficient is defined

    .. math::

       `\frac{g}{g-1}\frac{n-1}{n}`

    where g is the number of groups and n is the sample size.
    """
    n = clusters.shape[0]
    ngroups = np.unique(clusters).shape[0]
    return (ngroups / (ngroups - 1)) * ((n - 1) / n)


def cluster_union(clusters: NDArray) -> NDArray:
    """
    Compute a set of clusters that is nested within 2 clusters

    Parameters
    ----------
    clusters : ndarray
        A nobs by 2 array of integer values of cluster group membership.

    Returns
    -------
    ndarray
        A nobs array of integer cluster group memberships
    """
    sort_keys = np.lexsort(clusters.T)
    locs = np.arange(clusters.shape[0])
    lex_sorted = clusters[sort_keys]
    sorted_locs = locs[sort_keys]
    diff = np.any(lex_sorted[1:] != lex_sorted[:-1], 1)
    union = np.cumsum(np.r_[0, diff])
    resort_locs = np.argsort(sorted_locs)
    return union[resort_locs]


def cov_cluster(z: NDArray, clusters: NDArray) -> NDArray:
    """
    Core cluster covariance estimator

    Parameters
    ----------
    z : ndarray
        n by k mean zero data array
    clusters : ndarray
        n by 1 array

    Returns
    -------
    ndarray
       k by k cluster asymptotic covariance
    """

    num_clusters = len(unique(clusters))

    sort_args = argsort(clusters)
    clusters = clusters[sort_args]
    locs = where(r_[True, clusters[:-1] != clusters[1:], True])[0]
    z = z[sort_args]
    n, k = z.shape
    s = zeros((k, k))

    for i in range(num_clusters):
        st, en = locs[i], locs[i + 1]
        z_bar = z[st:en].sum(axis=0)[:, None]
        s += z_bar @ z_bar.T

    s /= n
    return s


def cov_kernel(z: NDArray, w: NDArray) -> NDArray:
    """
    Core kernel covariance estimator

    Parameters
    ----------
    z : ndarray
        n by k mean zero data array
    w : ndarray
        m by 1

    Returns
    -------
    ndarray
       k by k kernel asymptotic covariance
    """
    k = len(w)
    n = z.shape[0]
    if k > n:
        raise ValueError(
            "Length of w ({0}) is larger than the number "
            "of elements in z ({1})".format(k, n)
        )
    s = z.T @ z
    for i in range(1, len(w)):
        op = z[i:].T @ z[:-i]
        s += w[i] * (op + op.T)

    s /= n
    return s
