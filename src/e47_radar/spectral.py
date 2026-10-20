"""Fixed E47 spin-2 triple tensor-product construction."""
import numpy as np

CASIMIR = (0, 2, 6, 12, 20, 30, 42)
RANKS = (1, 9, 25, 28, 27, 22, 13)
DENOMINATOR = 99144

def spin_two():
    m = np.arange(2, -3, -1, dtype=float)
    plus = np.zeros((5, 5), dtype=complex)
    for k in range(1, 5):
        z = m[k]
        plus[k - 1, k] = np.sqrt((2 - z) * (2 + z + 1))
    minus = plus.conj().T
    return (plus + minus) / 2, (plus - minus) / (2j), np.diag(m).astype(complex)

def operators():
    I5 = np.eye(5, dtype=complex)
    Js = []
    for s in spin_two():
        Js.append(np.kron(np.kron(s, I5), I5)
                  + np.kron(np.kron(I5, s), I5)
                  + np.kron(np.kron(I5, I5), s))
    C = sum((j @ j for j in Js), np.zeros((125, 125), dtype=complex))
    w, v = np.linalg.eigh(C)
    projectors = {}
    for lam, rank in zip(CASIMIR, RANKS):
        mask = np.abs(w - lam) < 1e-7
        if np.count_nonzero(mask) != rank:
            raise ArithmeticError(f"Casimir shell {lam}: wrong multiplicity")
        u = v[:, mask]
        projectors[lam] = u @ u.conj().T
    P = projectors[6] + projectors[30]
    K = (C - 6 * np.eye(125)) @ (C - 30 * np.eye(125))
    Gamma = np.eye(125) - (K @ K) / DENOMINATOR
    return C, K, P, Gamma, projectors

def statistics(x, depths=(1, 2, 5)):
    """Return eta and r_n for rows of complex vectors. No label access."""
    x = np.asarray(x)
    if x.ndim != 2 or x.shape[1] != 125 or not np.iscomplexobj(x):
        raise ValueError("Expected complex array shape (N,125); real-valued input rejected")
    norm = np.sum(np.abs(x)**2, axis=1)
    if np.any(norm <= 0) or not np.all(np.isfinite(norm)):
        raise ValueError("Each input must be nonzero and finite")
    _, _, P, Gamma, _ = operators()
    eta = np.sum(np.abs(x @ P.T)**2, axis=1) / norm
    Q = np.eye(125) - P
    result = {"eta": eta}
    for n in depths:
        if not isinstance(n, int) or n < 0:
            raise ValueError("depth must be a nonnegative integer")
        op = Q @ np.linalg.matrix_power(Gamma, n)
        result[f"r{n}"] = np.sum(np.abs(x @ op.T)**2, axis=1) / norm
    return result
