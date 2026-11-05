# Two-block group-algebra inputs

The supplied archive uses H_X=[L(a)|R(b)] and H_Z=[R(b)^T|L(a)^T]. Column g is mapped to row a*g for L and g*b for R. These left/right actions commute even for non-abelian groups. The multiplication-table order and physical block order are preserved.

`ftqec validate-2bga code.json --output validation.json` verifies every associativity triple, identity, inverses, both regular actions, CSS commutation, dimension, and equality of the reconstructed full-check span to the independent input basis. The independent basis remains the external code representation; extraction measures all redundant group checks. Positive generator signs are required by this importer.

The 17 supplied files span n=24 to n=144. Algebraic validation succeeded on all 17. Independent exhaustive CSS support enumeration established d=4 for both n=24 codes and the [[36,8,4]] code. Other distance fields remain supplied claims, including solver-derived claims without independently checkable lower-bound evidence. The original archive, notes, and script are preserved locally and are not silently published.

Construction references: [Lin and Pryadko](https://arxiv.org/abs/2306.16400), [Bravyi et al.](https://www.nature.com/articles/s41586-024-07107-7). The precise convention above follows the supplied files, not a guessed generic bicycle convention.
