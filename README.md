# graph-visualizer
An alternative formulation derived from arbaregni's original program. 
This is an attempt to create nice looking images of graphs by treating the nodes as masses with forces acting between them,
then taking the longtime limit as we let the system evolve. 

The program named alt uses the strategy of placing typical springs (F = k(r-r0)) between each mass,
then adding a linear velocity dependent damping term (F = -bv) to make sure the system converges.

The program named atomic attempts to allow for more spread out stable distributions.
The forces are inspired by the behavior of protons and neutrons inside an atom, hence the name.
This is simulated using combination of s longdistance acting attractive coulomb force (prop to 1/r^2) 
and a repulsive strong force which dies off quickly (prop to 1/r^5) along with damping. 
Further work is needed since the system tends to prefer either oscillating 
right off the frame or getting damped before reaching a good looking final state.

Alt includes a section which converts the frames into a watchable video using imageio.

Work in progress!
