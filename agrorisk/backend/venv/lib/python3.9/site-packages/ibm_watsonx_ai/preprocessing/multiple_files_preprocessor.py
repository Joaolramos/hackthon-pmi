__all__ = [
    "DataJoinGraph"
]

#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.preprocessing.multiple_files_preprocessor import (BaseOBMJson, Node, Edge,
                                                                                    Table, DataJoinGraph)

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class BaseOBMJson(BaseOBMJson):
    """Base class for helper objects representation."""
    pass

@change_docstrings
class Node(Node):
    """Node class for json representation and conversion of graphviz nodes."""
    pass

@change_docstrings
class Edge(Edge):
    """Edge helper class for json representation of graphviz edge."""
    pass

@change_docstrings
class Table(Table):
    """Table class to represent / define OBM tables."""
    pass

@change_docstrings
class DataJoinGraph(DataJoinGraph):
    """DataJoinGraph class - helper class for handling multiple data sources for AutoAI experiment.

    You can define the overall relations between each of data source and see these defined relations
    in a form of string representation calling print(ObmGraph) or to leverage graphviz library
    and make entire graph visualization.

    :param t_shirt_size: the size of the computation POD
    :type t_shirt_size: enum TShirtSize, optional


    **Example**

    .. code-block:: python

        data_join_graph = DataJoinGraph()
        # or
        data_join_graph = DataJoinGraph(t_shirt_size=DataJoinGraph.TShirtSize.L)

        data_join_graph.node(name="main")
        data_join_graph.node(name="customers")
        data_join_graph.node(name="transactions")
        data_join_graph.node(name="purchases")
        data_join_graph.node(name="products")

        data_join_graph.edge(from_node="main", to_node="customers",
                             from_column=["group_customer_id"], to_column=["group_customer_id"])
        data_join_graph.edge(from_node="main", to_node="transactions",
                             from_column=["transaction_id"], to_column=["transaction_id"])
        data_join_graph.edge(from_node="main", to_node="purchases",
                             from_column=["group_id"], to_column=["group_id"])
        data_join_graph.edge(from_node="transactions", to_node="products",
                             from_column=["product_id"], to_column=["product_id"])

        print(data_join_graph)
        data_join_graph.visualize()
    """
    pass