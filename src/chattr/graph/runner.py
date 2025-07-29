from langgraph.graph.state import CompiledStateGraph

from chattr.graph.builder import Graph
from chattr.settings import Settings

graph: CompiledStateGraph = Graph(settings=Settings()).get_graph()