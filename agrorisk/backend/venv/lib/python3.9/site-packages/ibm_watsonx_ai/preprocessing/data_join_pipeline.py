__all__ = [
    'DataJoinPipeline',
    'OBMPipelineGraphBuilder'
]

#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2020- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------
import ast
import re
from operator import itemgetter
from .templates import pretty_print_template

from ibm_watson_machine_learning.preprocessing.data_join_pipeline import DataJoinPipeline, OBMPipelineGraphBuilder

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class DataJoinPipeline(DataJoinPipeline):
    """Class representing abstract data join pipeline."""
    def pretty_print(self, ipython_display: bool = False) -> None:
        """Print code which generates OBM data preprocessing.

        :param ipython_display: if method executed in jupyter notebooks/ipython set this flag to true in order
            to get syntax highlighting
        :type ipython_display: bool, optional
        """
        if hasattr(self, 'lale_pipeline'):
            if ipython_display:
                self.lale_pipeline.pretty_print(ipython_display=True)
            else:
                print(self.lale_pipeline.pretty_print())
        else:
            params = self._optimizer.get_params()
            data_join_graph = params["data_join_graph"]

            nodes = ""
            for node in data_join_graph.nodes:
                if node.table.timestamp_format and node.table.timestamp_column_name:
                    nodes += f"data_join_graph.node(name=\"{node.table.name}\"," \
                             f" timestamp_column_name=\"{node.table.timestamp_column_name}\"," \
                             f" timestamp_format=\"{node.timestamp_format}\")\n"
                else:
                    nodes += f"data_join_graph.node(name=\"{node.table.name}\")\n"

            edges = "\n".join([f"data_join_graph.edge(from_node=\"{edge.from_node}\", to_node=\"{edge.to_node}\",\n"
                               f"\t\t\t\t\t from_column={edge.from_column}, to_column={edge.to_column})"
                               for edge in data_join_graph.edges])

            join_indices = [it - 1 for it in self._obm_pipeline_graph_builder.get_join_iterations()]
            paths = "\n".join(["# - " + re.search(r"\[(.*)\]", msg["message"]["text"]).group()
                               for msg in itemgetter(*join_indices)(self._pipeline_json)])
            nb_of_features = re.search(r"\d", self._pipeline_json[-1]["message"]["text"]).group()

            pretty_print = pretty_print_template.template.format(
                nodes=nodes, edges=edges,
                name=f"\"{params['name']}\"",
                prediction_type=f"\"{params['prediction_type']}\"",
                prediction_column=f"\"{params['prediction_column']}\"",
                scoring=f"\"{params['scoring']}\"",
                paths=paths,
                nb_of_features=nb_of_features)

            if ipython_display:
                import IPython.display
                markdown = IPython.display.Markdown(f'```python\n{pretty_print}\n```')
                IPython.display.display(markdown)
            else:
                print(pretty_print)

@change_docstrings
class OBMPipelineGraphBuilder(OBMPipelineGraphBuilder):
    """Class for extracting particular elements from OBM output json with pipeline description.

    :param pipeline_json: dictionary with loaded obm.json file
    :type pipeline_json: dict
    """
    pass