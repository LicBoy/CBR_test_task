from lxml import etree
from utils.logger import logger
from typing import List, Set
import os

class XMLObject:
    """ Class for abstract XML doc with basic operations """
    def __init__(self, xml_path: str, namespace: str=None, encoding: str ='utf-8'):
        self.xml_path: str = xml_path
        self.tree: etree._ElementTree = self._load_xml_tree(encoding)
        self.namespace: dict = {"ns": namespace}

    def _load_xml_tree(self, encoding) -> etree._ElementTree:
        """Load and parse the XML file."""
        if not os.path.exists(self.xml_path):
            logger.error(f"XML file not found: {self.xml_path}")
            raise FileNotFoundError(f"XML file not found: {self.xml_path}")
        
        with open(self.xml_path, "r", encoding=encoding) as f:
            tree = etree.parse(f)
        return tree
    
    def find(self, path: str) -> etree._Element:
        return self.tree.find(path, namespaces=self.namespace)

    def find_all(self, path: str) -> List[etree._Element]:
        return self.tree.findall(path, namespaces=self.namespace)
    
    def find_text(self, path: str, default = None):
        return self.tree.findtext(path, default=default, namespaces=self.namespace)
    
    def get_element_children_elems(self, elem: etree._Element) -> List[etree._Element]:
        return elem.getchildren()
    
    def get_element_unique_children_names(self, elem: etree._Element, remove_namespace=True) -> Set[str]:
        results = [elem.tag for elem in self.get_element_children_elems(elem)]
        if remove_namespace:
            results = [elem.split('}')[1] for elem in results]
        return set(results)
    
    def all_given_nodes_contain_attrib(self, nodes_path: str, attrib_name: str):
        """
        Check that all nodes by given path contain given attribute.

        Returns tuple of    (True, *len of nodes total*) if all nodes contain attribute or
                            (False, *list of numbers of bad nodes*) if some nodes do not contain them.
        """
        logger.info(f"Checking that nodes '{nodes_path}' contain attribute '{attrib_name}'")
        found_nodes = self.find_all(nodes_path)
        bad_nodes = []
        for node_num, node in enumerate(found_nodes, start=1):
            if node.get(attrib_name) is None:
                bad_nodes.append(node_num)
        if len(bad_nodes) > 0:
            logger.info(f"Ids of nodes, which do not contain specified attribute: '{bad_nodes}'")
            return False, bad_nodes
        logger.info(f"All nodes contain specified attribute'")
        return True, len(found_nodes)
    
    def all_given_nodes_contain_one_of_attrib(self, nodes_path: str, *attrib_options):
        """
        Check that all nodes by given path contain one of given options as attribute.

        Returns tuple of    (True, *len of nodes total*) if all nodes contain only one of options or
                            (False, *list of numbers of bad nodes*) if some nodes contain options != 1.
        """
        logger.info(f"Checking that nodes '{nodes_path}' contain only one attribute of '{attrib_options}'")
        found_nodes = self.find_all(nodes_path)
        bad_nodes = []
        for node_num, node in enumerate(found_nodes, start=1):
            found_options = 0
            for cur_attrib in attrib_options:
                if node.get(cur_attrib) is not None:
                    found_options += 1
                    if found_options > 1:
                        break
            if found_options != 1:
                bad_nodes.append(node_num)
        if len(bad_nodes) > 0:
            logger.info(f"Ids of nodes, which contain not one attribute: '{bad_nodes}'")
            return False, bad_nodes
        logger.info(f"All nodes contain only one of specified attributes'")
        return True, len(found_nodes)
    
    def all_given_nodes_contain_child_node(self, nodes_path: str, child_node_name: str):
        """
        Check that all nodes by given path contain child with name.

        Returns tuple of    (True, *len of nodes total*) if all nodes contain child or
                            (False, *list of numbers of bad nodes*) if some nodes do not contain them.
        """
        logger.info(f"Checking that nodes '{nodes_path}' contain child node '{child_node_name}'")
        found_nodes = self.find_all(nodes_path)
        bad_nodes = []
        for node_num, node in enumerate(found_nodes, start=1):
            node_childs = self.get_element_unique_children_names(node)
            if child_node_name not in node_childs:
                bad_nodes.append(node_num)
        if len(bad_nodes) > 0:
            logger.info(f"Ids of nodes, which do not contain specified child: '{bad_nodes}'")
            return False, bad_nodes
        logger.info(f"All nodes contain specified child'")
        return True, len(found_nodes)

        
class BalanceXML(XMLObject):
    """ Class for balance XML with specific locators and operations """
    def __init__(self, xml_path: str, namespace: str=None, encoding: str ='utf-8'):
        super().__init__(xml_path, namespace, encoding)
        self.node_balance_locator = "ns:Ballance"
        self.node_operation_locator = f"{self.node_balance_locator}/ns:Oper"
        self.node_status_locator = "ns:Status"
        self.node_corrAcc_locator = "ns:corAcc"

    def check_all_operation_nodes_contain_date(self):
        return self.all_given_nodes_contain_attrib(self.node_operation_locator, "date")
    
    def check_all_operation_nodes_contain_corr_acc(self):
        return self.all_given_nodes_contain_attrib(self.node_operation_locator, "corAcc")
    
    def check_all_operation_nodes_contain_dbt_or_cdt(self):
        return self.all_given_nodes_contain_one_of_attrib(self.node_operation_locator, "dbt", "cdt")
    
    def check_all_operation_nodes_contain_status_node(self):
        return self.all_given_nodes_contain_child_node(self.node_operation_locator, "Status")
