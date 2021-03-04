import numpy as np
import functional_algebra as fa

fa.set_backend('numpy')

x = fa.variable('x')
y = fa.variable('y')
z = fa.variable('z')

r2 = (x**2 + y**2 + z**2)
r = r2**0.5
r2.give_name('r2')
psi = fa.exp(-r)
print(psi)
psi.give_name('psi')

x_val = np.random.rand(5)
y_val = np.random.rand(5)
z_val = np.random.rand(5)

values = [x>>x_val,y>>y_val,z>>z_val]

print("x: ")
print("psi:",psi.evaluate(values),'\n------------------------------\n')

T = -0.5*(psi.differentiate(x,x) + psi.differentiate(y,y) + psi.differentiate(z,z))
print("T:",T,'\n------------------------------\n')

V = -psi/r
print("V:",V,'\n------------------------------\n')

H = T+V

print("Ĥ: ",H,H.evaluate(values),'\n------------------------------\n')
print("ĤΨ/Ψ: ",H.evaluate(values)/psi.evaluate(values))
