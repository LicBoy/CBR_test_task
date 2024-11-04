from dataclasses import dataclass
from model.Operation import Operation
from utils.xml import BalanceXML
from utils.logger import logger

@dataclass
class Balance:
    """ Class for balance model for checking business logic """
    def __init__(self, self_corr_account: str, xml_tree_root: BalanceXML):
        self.corr_account = self_corr_account
        self.operations = self._parse_operation_nodes(xml_tree_root)
        self.total_processed_debit = self._calculate_processed_operation(is_debit=True)
        self.total_processed_credit = self._calculate_processed_operation(is_debit=False)
        
    def _parse_operation_nodes(self, xml_tree_root: BalanceXML) -> list[Operation]:
        operations = []
        for counter, oper in enumerate(xml_tree_root.find_all(xml_tree_root.node_operation_locator), start=1):
            operations.append(
                Operation(
                    id = counter,
                    date = oper.get("data"),
                    status = oper.findtext(xml_tree_root.node_status_locator, namespaces=xml_tree_root.namespace),
                    # Т.к. из-за бага 'corAcc' в некоторых элементах аттрибут, а в некоторых подэлемент, то собираем его так:
                    corr_account = oper.get("corAcc") or oper.findtext(xml_tree_root.node_corrAcc_locator, namespaces=xml_tree_root.namespace),
                    dbt = oper.get("dbt", default=''),
                    cdt = oper.get("cdt", default='')
                )
            )
        logger.info(f"Successfully parsed XML to Balance object with Operation entities")
        return operations
    
    def _calculate_processed_operation(self, is_debit: bool):
        assert self.each_operation_is_either_debit_or_credit()[0]
        assert self.each_operation_has_valid_amount()[0]
        total_amount = 0
        for oper in self.operations:
            if not oper.is_processed: # Хотя в инструкции про статусы ничего не сказано, но показалось логичным учитывать только заверешнные операции, т.е. со статусом "Выполнена"
                continue
            if is_debit and oper.debit_amount is None or not is_debit and oper.credit_amount is None:
                continue
            total_amount += oper.debit_amount if is_debit else oper.credit_amount
        logger.info(f"Total {"debit" if is_debit else "credit"} amount is '{total_amount}'")
        return total_amount
    
    def get_unique_dates(self):
        return set([oper.date.strftime("%d-%m-%Y") for oper in self.operations])
    
    def cor_accounts_are_different_from_our(self):
        logger.info(f"Checking that operation's cor accounts are different from our '{self.corr_account}'")
        bad_ids = []
        for oper in self.operations:
            if oper.corr_account == self.corr_account:
                bad_ids.append(oper.id)
        if len(bad_ids) > 0:
            logger.info(f"Ids of operations, which have same cor account as our '{bad_ids}'")
            return False, bad_ids
        logger.info(f"All operations have different cor acc from our!")
        return True, len(self.operations)

    def each_operation_is_either_debit_or_credit(self):
        logger.info(f"Checking that each operation is either debit or credit")
        bad_ids = []
        for oper in self.operations: # Only one of debit or credit should be != None
            if oper.credit_amount is None and oper.debit_amount is None or oper.credit_amount is not None and oper.debit_amount is not None:
                bad_ids.append(oper.id)
        if len(bad_ids) > 0:
            logger.info(f"Ids of operations, which are both debit and credit '{bad_ids}'")
            return False, bad_ids
        logger.info(f"All operations are either debit or credit!")
        return True, len(self.operations)
    
    def each_operation_has_valid_amount(self):
        logger.info(f"Checking that each operation is valid ( > 0)")
        bad_ids = []
        for oper in self.operations: # Only one of debit or credit should be != None
            if oper.credit_amount is not None and oper.credit_amount <= 0 or oper.debit_amount is not None and oper.debit_amount <= 0:
                bad_ids.append(oper.id)
        if len(bad_ids) > 0:
            logger.info(f"Ids of operations, which have invalid amount '{bad_ids}'")
            return False, bad_ids
        logger.info(f"All operations have valid amount!")
        return True, len(self.operations)
    
    
    