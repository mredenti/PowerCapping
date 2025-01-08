# SPECFEM3D 

Relevant Simulation Cases: https://www.nvidia.com/es-la/data-center/gpu-accelerated-applications/specfem3d-cartesian/

Red Hat: https://www.redhat.com/en/blog/a-complete-guide-for-running-specfem-scientific-hpc-workload-on-red-hat-openshift

## GLOBE? Test case 

## Both GPU and CPU 



# Forward and Adjoint Simulations of Seismic Wave Propagation Based on the Spectral Element Method


## Seismological Forward Problem

$$ 
    \partial_t^2 s - \nabla . \bf{T} = f
$$

- $T = c:\epsilon$ [Constitutive relationship (Hooke's Law)]. In Specfem the tensor can be completely general, meaning it can have 21 independent elastic coefficients. However, most of the time they look at an isotropic material for which we have just two elastic parameters. 

- Boundary condition: $\hat{n} \cdot \bf{T} = 0$ i.e. the earth is a stress free surface

- Initial Conditions: $\bf{s}(x, 0) = 0$ and $\partial_t \bf{s}(x, 0) = 0$

- Earthquake Source: $\bf{f} = - \bf{M} \cdot \nabla \delta (\bf{x} - \bf{x_s} ) S(t)$
  - The moment tensor M represents a slip on a fault, x_s is the source location and S(t) is the source time function [double couple source]

The above problem statement is the full set of equations that needs to be solved if you want to propagate seismic wave in an elastic medium (2d, 3d, ...v )


## Spectral-Element Method 

Finite-elements (all calcolations are local and so they scale extremely well on parallel machines so that there are not long-range interactions): 

- Hexahedral elements  
- Gauss-Lobatto-Legendre quadrature
- $\Rightarrow$ Diagonal Mass Matrix $\Rightarrow$ Explicit time-marching scheme
- $M\doubledot{U} + C \dot{U} + KU = F$


## Open Source Forward & Inverse Modelling Software (see [Computational Infrastructure for Geodynamics](www.geodynamics.org))

- SPECFEM3D 
- SPECFEM3D_GLOBE

for 3d crust and mantle models, can account for the rotation of the earth, topography & bathymetry, ellipticity of the earth, gravitation, anisotropy, attenuation, adjoint capabilities (crucial for inverse problems, calculate the gradient of a missfit function, all packages are GPU accelerated)




## Meeting per Spiga: 

- Al momento non ha piu di tanto senso contattare gli sviluppatori per chiedere quale test case sia utile e molto probabilmente si sono più test case di interesse. Ora assumendo che girare un particolare test case piuttosto che un altro non richieda la compilazione di codice completamente diverso ma comuqnue un numero di righe modico (per esempio basterebbe variare un input file), il mio piano di attacco iniziale sarebbe quello di iniziare a compilare i seguenti codici alla ultima versione disponibile e far girare i test:
  
  - specfem3d globe
  - specfem3d 
  - specfem2d
  - specfem-mini 

  - fall3d

  - tandem/xshells


# Geometric Intuition 

Intuitive Picture of the Seismic Wave Equation:

When we talk about seismic waves traveling through the Earth, we're considering how small parcels of rock or fluid move back and forth when a disturbance (like an earthquake) passes through. Imagine tapping one end of a long, three-dimensional block of material—this disturbance will spread out as a wave. The seismic wave equation is a mathematical description of how these tiny motions evolve over time. In essence, it tells us how the material’s particles move in response to forces caused by their neighbors also moving.

In fluids and solids, these waves propagate because small displacements in one region create stresses (or pressures) that push on neighboring regions, causing them to move as well. This cascades through the material, much like how a ripple spreads across the surface of a pond. The seismic wave equation we use encapsulates this relationship between displacement, velocity, acceleration, and the internal forces (stresses) that arise from these motions.

Stress Tensor:

The concept of “stress” is central in understanding how waves move inside a material. We can think of “stress” as the internal force per unit area within the material. For example, if you push on one side of a block of rubber, every tiny square inside that block will feel some pushing or pulling force acting on it. But this force doesn’t just act in one direction; it can act in multiple directions depending on how the material is being distorted.

To describe these forces at a point in a material, we use a stress tensor. A tensor can be thought of as a structured way of keeping track of how something varies with direction. In three-dimensional space, the stress tensor is like a 3×3 grid of numbers that tells you, for any tiny square surface you imagine at a point, what the force per unit area is acting on it, and in which direction.

Imagine choosing a small cubic element in the material. This cube has six faces, and on each face there might be a force pushing or pulling. The stress tensor organizes all of these internal "pushes" and "pulls" into a single mathematical object.
Each entry of the stress tensor corresponds to how much force is acting in a certain direction on a surface oriented in a certain direction. For example, one part of the tensor tells you how strongly the material is being pulled in the x-direction on a face that is perpendicular to the x-axis, while another part might tell you about shearing forces—pulls in the y-direction on a surface oriented along the x-axis, and so on.
Taking the Divergence of the Stress Tensor:

The “divergence” of something in mathematics gives a measure of how much that “thing” spreads out from a point. When we take the divergence of a vector field (like velocity or a force field), we get a scalar that tells us how much of that vector field is flowing out of or into a point.

However, stress is not just a vector—it's a tensor. The divergence of the stress tensor results in a vector that tells you the net force per unit volume acting at every point. Here’s how to understand that:

Start with the stress tensor, which describes the internal forces on all possible little surfaces at a point.
Taking the divergence (a kind of spatial derivative) of the stress tensor is like asking: “If I look around this tiny point in all directions, do these internal pushes and pulls balance out, or do they leave a net force behind?”
If the stresses on all sides balance perfectly, the divergence is zero—no net force at that point. If they don’t balance, the divergence is non-zero, meaning there’s a net unbalanced force at that location.
Geometrically, imagine placing a tiny imaginary sphere inside the material. The stress tensor describes how that sphere is being squeezed, stretched, or sheared by the surrounding material. If you “sum up” (integrate) all these small stresses over the sphere’s surface, you end up with a total pushing or pulling on the sphere. The divergence of the stress tensor is essentially the limit of this integrated force per unit volume as the sphere gets very small, telling you at that point if there’s a net force directing how the material should accelerate.

Connecting it All:

The seismic wave equation comes from applying Newton’s second law (force equals mass times acceleration) at every point in a continuous material. Because the net force per unit volume can be expressed as the divergence of the stress tensor, we get an equation that relates how acceleration (changes in displacement or velocity) arises from stresses. When combined with how the material responds to deformation (through its constitutive laws, like Hooke’s law for an elastic solid), we end up with a set of wave equations. These equations govern how disturbances propagate—how seismic waves travel and change shape as they move through varying layers of rock or fluid inside the Earth.






