from utils.logger import logger
from utils.xml import BalanceXML
from model.Balance import Balance
from pytest_check import check


class TestBalanceXMLStructure:
    def test_balance_node_exist(self, balance_xml_tree: BalanceXML):
        search_result = balance_xml_tree.find("ns:Balance")
        logger.info(f"Search result for 'Balance' node: {search_result}")
        assert search_result is not None, "Balance XML should contain 'Balance' as node"

    def test_balance_has_operation_children(self, balance_xml_tree: BalanceXML):
        unique_child_nodes = balance_xml_tree.get_element_unique_children_names(
            balance_xml_tree.find(balance_xml_tree.node_balance_locator)
        )
        
        with check:
            assert "Operation" in unique_child_nodes, "Balance node should contain children called 'Operation'"
        with check:
            assert len(unique_child_nodes) == 1, "Balance node should contain only 1 type of children which is 'Operation'"

    def test_operation_node_contains_attrib_date(self, balance_xml_tree: BalanceXML):
        check_result, check_descr = balance_xml_tree.check_all_operation_nodes_contain_date()
        assert check_result, \
            f"All nodes should contain attribute 'date'. Found nodes without it: {check_descr}!"

    def test_operation_node_contains_attrib_corAcc(self, balance_xml_tree: BalanceXML):
        check_result, check_descr = balance_xml_tree.check_all_operation_nodes_contain_corr_acc()
        assert check_result, \
            f"All nodes should contain attribute 'corAcc'. Found nodes without it: {check_descr}!"

    def test_operation_node_contains_attrib_one_of_dbt_cdt(self, balance_xml_tree: BalanceXML):
        check_result, check_descr = balance_xml_tree.check_all_operation_nodes_contain_dbt_or_cdt()
        assert check_result, \
            f"All nodes should contain only one of attributes 'dbt' or 'cdt'. Found bad nodes: {check_descr}!"
        
    def test_operation_node_contains_subNode_with_status(self, balance_xml_tree: BalanceXML):
        check_result, check_descr = balance_xml_tree.check_all_operation_nodes_contain_status_node()
        assert check_result, \
            f"All nodes should contain child node 'Status'. Found nodes without it: {check_descr}!"



class TestBalanceBusinessLogic:
    def test_all_operations_happened_one_date(self, balance: Balance):
        unique_dates = balance.get_unique_dates()
        assert len(unique_dates) == 1, \
            f"Expected all operations to happen on one date, but found multiple: {unique_dates}!"
        
    def test_corr_accounts_are_different_from_our(self, balance: Balance):
        check_result, check_descr = balance.cor_accounts_are_different_from_our()
        assert check_result, \
            f"All operations should have different corr account from our! These operations have same corr account: {check_descr}!"
        
    def test_operation_amounts_are_correct(self, balance: Balance):
        check_result, check_descr = balance.each_operation_is_either_debit_or_credit()
        assert check_result, \
            f"All operations should be either debit or credit! These operations are not correct: {check_descr}!"
        
    def test_operation_amounts_are_valid(self, balance: Balance):
        check_result, check_descr = balance.each_operation_has_valid_amount()
        assert check_result, \
            f"All operations should have valid amount ( > 0)! These operation amounts are not correct: {check_descr}!"
        
    def test_application_difference_is_correct(self, application_balances: dict):
        assert application_balances["difference"] == application_balances["debit_total"] - application_balances["credit_total"], \
            f"Difference between debit and credit amount in application expected to be {application_balances["debit_total"] - application_balances["credit_total"]}, but got '{application_balances["difference"]}'!"
        
    def test_application_and_balance_total_debit_are_equal(self, application_balances: dict, balance: Balance):
        application_total_debit = application_balances["debit_total"]
        assert application_total_debit == balance.total_processed_debit, \
            f"Total debit amounts from application and all XML operations should be equal!"
        
    def test_application_and_balance_total_credit_are_equal(self, application_balances: dict, balance: Balance):
        application_total_debit = application_balances["credit_total"]
        assert application_total_debit == balance.total_processed_credit, \
            f"Total credit amounts from application and all XML operations should be equal!"
        