import numpy as np
import functional_algebra as fa

np.random.seed(0)

fa.set_backend('numpy')

x = fa.variable('x')
y = fa.variable('y')
z = fa.variable('z')

r2 = (x**2 + y**2 + z**2)
r = r2**0.5
r2.give_name('r2')

def H(psi):
    return -0.5*(psi.differentiate(x,x)+psi.differentiate(y,y)+psi.differentiate(z,z)) - psi/r

psi = fa.exp(-r)
print(psi)
psi.give_name('psi')

x_val = np.random.rand(5)
y_val = np.random.rand(5)
z_val = np.random.rand(5)

values = [x>>x_val,y>>y_val,z>>z_val]

print("x: ")
print("Ψ₁₀₀:",psi.evaluate(values),'\n------------------------------\n')

T = -0.5*(psi.differentiate(x,x) + psi.differentiate(y,y) + psi.differentiate(z,z))
print("T₁₀₀:",T,'\n------------------------------\n')

V = -psi/r
print("V₁₀₀:",V,'\n------------------------------\n')

H = T+V

print("Ĥ₁₀₀: ",H,H.evaluate(values),'\n------------------------------\n')
print("Ĥ₁₀₀Ψ/Ψ: ",H.evaluate(values)/psi.evaluate(values))

print('\n------------------------------\n')

psi200 = (2-r)*fa.exp(-r/2)

T200 = -0.5*(psi200.differentiate(x,x) + psi200.differentiate(y,y) + psi200.differentiate(z,z))
V200 = -psi200/r
H200 = T200 + V200

print("ĤΨ₂₀₀/Ψ₂₀₀: ", H200.evaluate(values)/psi200.evaluate(values))

print('\n------------------------------\n')

phi = fa.arctan2(y,x)
theta = fa.arccos(z/r)

alt = z*fa.exp(-r/2)
psi210 = fa.cos(theta)*r*fa.exp(-r/2)
psi210.give_name('Ψ₂₁₀')

T210 = -0.5*(psi210.differentiate(x,x) + psi210.differentiate(y,y) + psi210.differentiate(z,z))
V210 = -psi210/r
H210 = T210 + V210

print("ĤΨ₂₁₀/Ψ₂₁₀: ", H210.evaluate(values)/psi210.evaluate(values))

print('\n------------------------------\n')

psi211 = fa.exp(1j*phi)*fa.sin(theta)*r*fa.exp(-r/2)

T211 = -0.5*(psi211.differentiate(x,x) + psi211.differentiate(y,y) + psi211.differentiate(z,z))
V211 = -psi211/r
H211 = T211 + V211

print("ĤΨ₂₁₁/Ψ₂₁₁: ",H211.evaluate(values)/psi211.evaluate(values))
