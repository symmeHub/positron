Core
------------

Core regroups the general purpose tools of the Truss package.

Nodes
+++++++

.. autoclass:: truss.core.Node
.. automethod:: truss.core.Node.data


Bars
+++++++

.. autoclass:: truss.core.Bar
.. automethod:: truss.core.Bar.data
.. automethod:: truss.core.Bar.length
.. automethod:: truss.core.Bar.volume
.. automethod:: truss.core.Bar.mass
.. automethod:: truss.core.Bar.direction
.. automethod:: truss.core.Bar.normal
.. automethod:: truss.core.Bar.stiffness
.. automethod:: truss.core.Bar.stiffness_matrix



Models
+++++++

.. autoclass:: truss.core.Model
.. automethod:: truss.core.Model.data
.. automethod:: truss.core.Model.add_node
.. automethod:: truss.core.Model.add_bar
.. automethod:: truss.core.Model.add_node
.. automethod:: truss.core.Model.add_force
.. automethod:: truss.core.Model.stiffness_matrix
.. automethod:: truss.core.Model.force_vector
.. automethod:: truss.core.Model.solve
.. automethod:: truss.core.Model.active_dof
.. automethod:: truss.core.Model.bbox
.. automethod:: truss.core.Model.draw




