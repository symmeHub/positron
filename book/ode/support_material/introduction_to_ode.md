# Numerical solutions of ordinary differential equations

The problem of solving differential equations is not just a mathematical concern. 
Many physical equations that describe the evolution and equilibrium of very diverse systems are differential equations. 
There are two types of differential equations: 

* **Ordinary Differential Equations** (ODE) in which the function being sought depends only on one variable, usually time $t$. 
* **Partial Differential Equations** in which it also depends on other variables, usually space. 

In this course, we are only interested in ordinary differential equations.
The notions discussed and the observations made are also largely applicable to partial differential equations. 


## ODE formulation

As an example, we can consider the case of a free and undamped oscillator. 
Its motion is described by the following equation:

```{math}
:label: undamped_oscillator_ode
\ddot x + \omega_0^2 x = 0
```
An ODE can be described by several characteristics.
In particular:

* Its order: here the equation is of second order.
* Its number of equations: depending on the problem, only one here but many ODEs can be presented as systems of equations.
* The explicit time dependence. If this one does not appear, the equation is said to be autonomous. 
* Linearity: if the unknown function and its derivatives appear only multiplied by constants, then the equation is linear. 
On the contrary, for example if they appear to a power other than 1 or in a sine, then the equation is non-linear. 
Here the equation is linear.



## Solving ODEs 
