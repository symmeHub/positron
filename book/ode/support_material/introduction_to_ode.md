# Numerical solutions of ordinary differential equations

The problem of solving differential equations is not just a mathematical concern. 
Many physical equations that describe the evolution and equilibrium of very diverse systems are differential equations. 
There are two types of differential equations: 

* **Ordinary Differential Equations** (ODE) in which the function being sought depends only on one variable, usually time $t$. 
* **Partial Differential Equations** in which it also depends on other variables, usually space. 

In this course, we are only interested in ordinary differential equations.
The notions discussed and the observations made are also largely applicable to partial differential equations. 

```{note}
This course is not a background paper on the underlying mathematical concepts. 
It is intended to provide the scientist with the necessary notions to make choices regarding the treatment of ODEs.
```

## ODE formulation

::::{admonition} ODE reformulation
:class: tip
As an example, we can consider the case of a free and undamped oscillator. 
Its motion is described by the following equation:
:::{math}
:label: undamped_oscillator_ode
\ddot x + \omega_0^2 x = 0
:::
::::
An ODE can be described by several characteristics.
In particular:

* Its order: here the equation is of second order.
* Its number of equations: depending on the problem, only one here but many ODEs can be presented as systems of equations.
* The explicit time dependence. If this one does not appear, the equation is said to be autonomous. 
* Linearity: if the unknown function and its derivatives appear only multiplied by constants, then the equation is linear. 
On the contrary, for example if they appear to a power other than 1 or in a sine, then the equation is non-linear. 
Here the equation is linear.

Depending on these characteristics, an equation will or will not have an exact known solution.
Only a minority of them have such a solution. 
Although they are not the subject of this course, the exact solutions will serve as a reference to test the approximate solutions.


To address ODEs on a systematic basis, a generic formulation is usually used that takes the form:

```{math}
:label: ode_generic
\dot X = f(X, t)
```

Where:
* $X: t \mapsto X(t) = [X_0(t),\dots, X_{N-1}(t)]^T $ is the unknown function.
* $f$ is the ODE 

This formulation is both simple and surprising, it implies that all ODEs can be written as first order equations. 
Of course, this advantage has a price: the decrease of the order goes through an increase of the number of equations through the creation of intermediate functions. 



```{admonition} ODE reformulation
:class: tip
From a practical point of view, formulating a problem in this way can take a bit of practice.
Let's take the example of the equation {eq}`undamped_oscillator_ode`.  
```
The unknown function $x$ can be replaced by a vector function:

:::{math}
X = [x, \dot x]^T 
:::

L'équation se réécrit

:::{math}
:label: undamped_linear_oscillator_rewritten
\underbrace{\begin{bmatrix}
\dot x \\
\ddot x
\end{bmatrix}}_{\dot X}
 = 
\underbrace{\begin{bmatrix}
X[1] \\
- \omega_0^2 X[0]
\end{bmatrix}}_{f(X, t)}

:::
## Solving ODEs 
