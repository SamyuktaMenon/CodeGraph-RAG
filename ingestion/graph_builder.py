from backend.db_neo4j import get_neo4j_driver
from typing import List, Dict, Any

class KnowledgeGraphBuilder:
    def __init__(self):
        self.driver = get_neo4j_driver()

    def build_graph(self, nodes: List[Dict[str, Any]], relationships: List[Dict[str, Any]] = None):
        with self.driver.session() as session:
            for node in nodes:
                session.execute_write(self._create_node, node)
            if relationships:
                for rel in relationships:
                    session.execute_write(self._create_relationship, rel)

    @staticmethod
    def _create_node(tx, node_data: Dict[str, Any]):
        node_type = node_data.get("type", "Entity")
        query = (
            f"MERGE (n:{node_type} {{name: $name, file_path: $file_path}}) "
            "SET n.docstring = $docstring, n.line_number = $line_number"
        )
        tx.run(query, 
               name=node_data.get("name"), 
               file_path=node_data.get("file_path"),
               docstring=node_data.get("docstring"),
               line_number=node_data.get("line_number"))

    @staticmethod
    def _create_relationship(tx, rel_data: Dict[str, Any]):
        rel_type = rel_data.get("type", "RELATED_TO")
        query = (
            f"MATCH (a {{name: $source}}) "
            f"MATCH (b {{name: $target}}) "
            f"MERGE (a)-[r:{rel_type}]->(b)"
        )
        tx.run(query, source=rel_data.get("source"), target=rel_data.get("target"))

    def close(self):
        self.driver.close()
