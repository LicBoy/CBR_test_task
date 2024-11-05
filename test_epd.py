from utils.xml import XMLObject
from utils.logger import logger
from utils.check import *
from pytest_check import check

ED101 = "ED101"
EDQUANTITY = "EDQuantity"
EDDATE = "EDDate"
EDAUTHOR = "EDAuthor"
EDNO = "EDNo"
SUM = "Sum"

SYSTEMCODE = "SystemCode"
EXPECTED_SYSTEMCODE_VAL = "01"

PAYER = "Payer"
PAYEE = "Payee"
BANK = "Bank"
BIC = "BIC"
CORRESPACC = "CorrespAcc"

BICDIRECTORYENTRY = "BICDirectoryEntry"
PARTICIPANTINFO = "ParticipantInfo"
ACCOUNT = "Account"
ACCOUNTS = "Accounts"
ACCDOC = "AccDoc"
ACCDOCNO = "AccDocNo"
ACCDOCDATE = "AccDocDate"
NAME = "Name"
PTTYPE = "PtType"
DATEIN = "DateIn"
RGN = "Rgn"
NAMEP = "NameP"


class TestPacketEPD:
    def test_root_headers_mandatory_values_equal_ed807(self, config, ed807_xml_tree: XMLObject, epd_xml_tree: XMLObject):
        ED807_mandatory_attributes = config["ed807_xml"]["header_mandatory_attributes"]
        ed807_header_all_attribs = ed807_xml_tree.get_root_attributes()
        epd_header_all_attribs = epd_xml_tree.get_root_attributes()
        for attrib in ED807_mandatory_attributes:
            with check:
                logger.info(f"Checking that attribute '{attrib}' is in ED807 XML document header")
                assert attrib in ed807_header_all_attribs, \
                    f"ED807 XML document should contain mandatory field '{attrib}'"
                
                logger.info(f"Checking that attribute '{attrib}' is in PacketEPD XML document header")
                assert attrib in epd_header_all_attribs, \
                    f"PacketEPD XML document should contain mandatory field '{attrib}'"
                
                if attrib in ed807_header_all_attribs and attrib in epd_header_all_attribs: # Check only if first 2 asserts passed, otherwise error occurs on item accessing
                    logger.info(f"Checking that attribute '{attrib}' is same in both ED807 XML and PacketEPD XML headers")
                    assert ed807_header_all_attribs[attrib] == epd_header_all_attribs[attrib], \
                        f"PacketEPD XML document should contain mandatory field '{attrib}'"
                    
    def test_root_headers_EDQuantity_equals_ed101_amount(self, epd_xml_tree: XMLObject):
        logger.info(f"Checking that attribute '{EDQUANTITY}' is equal to amount of {ED101} documents")
        epd_header_all_attribs = epd_xml_tree.get_root_attributes()
        ed101_elements = epd_xml_tree.find_all(ED101)

        assert EDQUANTITY in epd_header_all_attribs, \
            f"PacketEPD XML header should contain '{EDQUANTITY}' attribute!"
        
        assert int(epd_header_all_attribs[EDQUANTITY]) == len(ed101_elements), \
            f"PacketEPD XML header '{EDQUANTITY}' attribute should be equal to amount of '{ED101}' elements!"
        
    def test_root_headers_Sum_equals_ed101_sum(self, epd_xml_tree: XMLObject):
        logger.info(f"Checking that attribute '{SUM}' is equal to sum of all {ED101} document {SUM} attributes")
        epd_header_all_attribs = epd_xml_tree.get_root_attributes()
        ed101_elements = epd_xml_tree.find_all(ED101)

        assert EDQUANTITY in epd_header_all_attribs, \
            f"PacketEPD XML header should contain '{SUM}' attribute!"

        check_result, check_descr = epd_xml_tree.all_given_nodes_contain_attrib(ED101, SUM)
        assert check_result, \
            f"Each {ED101} doc should contain attribute '{SUM}'. But found bad docs: {check_descr}"
        
        ed101_sums = [int(elem.get(SUM)) for elem in ed101_elements]
        assert int(epd_header_all_attribs[SUM]) == sum(ed101_sums), \
            f"PacketEPD XML header '{SUM}' attribute should be equal to sum of all '{ED101}' elements' '{SUM}' attribute!"
        
    def test_SystemCode_is_correct_everywhere(self, epd_xml_tree: XMLObject):
        logger.info(f"Checking that '{SYSTEMCODE}' is equal '{EXPECTED_SYSTEMCODE_VAL}' in all elements")
        with check:
            assert SYSTEMCODE in epd_xml_tree.get_root_attributes(), \
                f"Tree root element should contain '{SYSTEMCODE}' attribute!"
            
            assert epd_xml_tree.get_root_attributes().get(SYSTEMCODE) == EXPECTED_SYSTEMCODE_VAL, \
                f"Attribute '{SYSTEMCODE}' of tree root element should be equal to '{EXPECTED_SYSTEMCODE_VAL}'!"
                
            ed101_elements = epd_xml_tree.find_all(ED101)
            for counter, ed101 in enumerate(ed101_elements, start=1):
                ed101_system_code_val = ed101.get(SYSTEMCODE)
                assert ed101_system_code_val == EXPECTED_SYSTEMCODE_VAL, \
                    f"Attribute '{SYSTEMCODE}' of {ED101} element №{counter} should be equal to '{EXPECTED_SYSTEMCODE_VAL}'!"
                
    def test_ED101_date_author_are_equal_to_header(self, epd_xml_tree: XMLObject):
        epd_header_all_attribs = epd_xml_tree.get_root_attributes()
        epd_header_date = epd_header_all_attribs[EDDATE]
        epd_header_author = epd_header_all_attribs[EDAUTHOR]
        ed101_elements = epd_xml_tree.find_all(ED101)

        logger.info(f"Checking that all {ED101} documents have attribute {EDDATE} equal to one in header")
        logger.info(f"Checking that all {ED101} documents have attribute {EDAUTHOR} equal to one in header")
        for counter, ed101 in enumerate(ed101_elements, start=1):
            ed101_date_attrib_val = ed101.get(EDDATE)
            ed101_author_attrib_val = ed101.get(EDAUTHOR)
            with check:
                assert ed101_date_attrib_val == epd_header_date, \
                    f"Attribute '{EDDATE}' of {ED101} element №{counter} should be equal to '{epd_header_date}'!"
                assert ed101_author_attrib_val == epd_header_author, \
                    f"Attribute '{EDAUTHOR}' of {ED101} element №{counter} should be equal to '{epd_header_author}'!"

    def test_ED101_EDNo_increments_by_one(self, epd_xml_tree: XMLObject):
        INCREASE_AMOUNT = 1
        logger.info(f"Checking that attribute '{EDNO}' increases by {INCREASE_AMOUNT} with each {ED101} document")
        ed101_elements = epd_xml_tree.find_all(ED101)
        for counter, ed101 in enumerate(ed101_elements, start=1):
            ed101_edno_attrib_val = int(ed101.get(EDNO))
            assert ed101_edno_attrib_val == counter, \
                f"Attribute '{EDNO}' of {ED101} element №{counter} should be equal to {counter}!"
            
    def test_ED101_has_required_requisites(self, epd_xml_tree: XMLObject):
        logger.info(f"Checking that all {ED101} documents have required requisites: {BIC} and {CORRESPACC}")
        ed101_elements = epd_xml_tree.find_all(ED101)
        payer_elements = [elem.find(PAYER).find(BANK) for elem in ed101_elements]
        payee_elements = [elem.find(PAYEE).find(BANK)  for elem in ed101_elements]

        for counter, payer in enumerate(payer_elements, start=1):
            payer_bic_attrib_val = payer.get(BIC)
            payer_correspAcc_attrib_val = payer.get(CORRESPACC)

            assert payer_bic_attrib_val != None, \
                f"{PAYER} №{counter} should contain attribute for required requisite {BIC}!"
            
            assert payer_correspAcc_attrib_val != None, \
                f"{PAYER} №{counter} should contain attribute for required requisite {CORRESPACC}!"
            
        for counter, payee in enumerate(payee_elements, start=1):
            payee_bic_attrib_val = payee.get(BIC)
            payee_correspAcc_attrib_val = payee.get(CORRESPACC)

            assert payee_bic_attrib_val != None, \
                f"{PAYEE} №{counter} should contain attribute for required requisite {BIC}!"
            
            assert payee_correspAcc_attrib_val != None, \
                f"{PAYEE} №{counter} should contain attribute for required requisite {CORRESPACC}!"
        
    def test_ED101_payer_and_payee_filled_from_BICDirectoryEntry(self, ed807_xml_tree: XMLObject, epd_xml_tree: XMLObject):
        logger.info(f"Checking that all {ED101} elements are filled correctly from {BICDIRECTORYENTRY} elements")
        ed101_elements = epd_xml_tree.find_all(ED101)
        ed101_AccDoc_elements = [elem.find(ACCDOC) for elem in ed101_elements]
        ed101_payer_elements = [elem.find(PAYER) for elem in ed101_elements]
        ed101_payee_elements = [elem.find(PAYEE) for elem in ed101_elements]

        ed807_entries = ed807_xml_tree.find_all(BICDIRECTORYENTRY)
        if len(ed807_entries) % 2 == 1:
            ed807_entries.pop() # Если для последнего ED101 нет записи для формирования получателя (ed:Payee), то игнорируем – не добавляем данный полуфабрикат ED101 в пакет PacketEPD
        ed807_ParticipantInfo_elements = [ed807_xml_tree.find(PARTICIPANTINFO, elem=elem) for elem in ed807_entries]
        ed807_accounts_elements = [ed807_xml_tree.find(ACCOUNTS, elem=elem) for elem in ed807_entries]

        payer_payee_pair_counter = 0
        errors_list = []
        for i in range(0, len(ed807_entries), 2):
            i_numeration = i + 1
            payer_payee_pair_counter_numeration = payer_payee_pair_counter + 1

            ed807_bic_entry_for_payer = ed807_entries[i]
            ed807_partinfo_entry_for_payer = ed807_ParticipantInfo_elements[i]
            ed807_accounts_entry_for_payer = ed807_accounts_elements[i]

            check_error(True, ed807_accounts_entry_for_payer is not None, errors_list,
                f"ED807 {BICDIRECTORYENTRY} at position {i_numeration} should contain {ACCOUNTS} element!",
                dont_continue=True
            )

            ed807_bic_entry_for_payee = ed807_entries[i+1]
            ed807_partinfo_entry_for_payee = ed807_ParticipantInfo_elements[i+1]
            ed807_accounts_entry_for_payee = ed807_accounts_elements[i+1]

            check_error(True, ed807_accounts_entry_for_payee is not None, errors_list,
                f"ED807 {BICDIRECTORYENTRY} at position {i_numeration+1} should contain {ACCOUNTS} element!",
                dont_continue=True
            )

            check_error(True, payer_payee_pair_counter < len(ed101_elements), errors_list,
                f"ED101 elements ended, but size should be enough to cover all {BICDIRECTORYENTRY} elements!",
                dont_continue=True
            )

            ed101_AccDoc = ed101_AccDoc_elements[payer_payee_pair_counter]
            ed101_payer = ed101_payer_elements[payer_payee_pair_counter]
            ed101_payee = ed101_payee_elements[payer_payee_pair_counter]

            # Check payer side
            check_error(ed101_AccDoc.get(ACCDOCNO), ed807_partinfo_entry_for_payer.get(PTTYPE), errors_list,
                f"ED101 {payer_payee_pair_counter_numeration} element's {ACCDOCNO} should be equal to ED807 {i_numeration} element's {PTTYPE}!\n" + 
                f"ED101 val = {ed101_AccDoc.get(ACCDOCNO)}, ED807 val = {ed807_partinfo_entry_for_payer.get(PTTYPE)}"
            )
            check_error(ed101_AccDoc.get(ACCDOCDATE), ed807_partinfo_entry_for_payer.get(DATEIN), errors_list,
                f"ED101 {payer_payee_pair_counter_numeration} element's {ACCDOCDATE} should be equal to ED807 {i_numeration} element's {DATEIN}!\n" + 
                f"ED101 val = {ed101_AccDoc.get(ACCDOCDATE)}, ED807 val = {ed807_partinfo_entry_for_payer.get(DATEIN)}"
            )
            check_error(ed101_elements[payer_payee_pair_counter].get(SUM), ed807_partinfo_entry_for_payer.get(RGN), errors_list,
                f"ED101 {payer_payee_pair_counter_numeration} element's {SUM} should be equal to ED807 {i_numeration} element's {RGN}!\n" + 
                f"ED101 val = {ed101_elements[payer_payee_pair_counter].get(SUM)}, ED807 val = {ed807_partinfo_entry_for_payer.get(RGN)}"
            )
            check_error(ed101_payer.findtext(NAME), ed807_partinfo_entry_for_payer.get(NAMEP), errors_list,
                f"ED101 {payer_payee_pair_counter_numeration} element's payer {NAME} should be equal to ED807 {i_numeration} element's {NAMEP}!\n" + 
                f"ED101 val = {ed101_payer.findtext(NAME)}, ED807 val = {ed807_partinfo_entry_for_payer.get(NAMEP)}"
            )
            check_error(ed101_payer.find(BANK).get(BIC), ed807_bic_entry_for_payer.get(BIC), errors_list,
                f"ED101 {payer_payee_pair_counter_numeration} element's payer {BIC} should be equal to ED807 {i_numeration} element's {BIC}!\n" + 
                f"ED101 val = {ed101_payer.find(BANK).get(BIC)}, ED807 val = {ed807_bic_entry_for_payer.get(BIC)}"
            )
            check_error(ed101_payer.find(BANK).get(CORRESPACC), ed807_accounts_entry_for_payer.get(ACCOUNT), errors_list,
                f"ED101 {payer_payee_pair_counter_numeration} element's payer {CORRESPACC} should be equal to ED807 {i_numeration} element's {ACCOUNT}!\n" + 
                f"ED101 val = {ed101_payer.find(BANK).get(CORRESPACC)}, ED807 val = {ed807_accounts_entry_for_payer.get(ACCOUNT)}"
            )

            # Check payee side
            check_error(ed101_payee.findtext(NAME), ed807_partinfo_entry_for_payee.get(NAMEP), errors_list,
                f"ED101 {payer_payee_pair_counter_numeration} element's payee {NAME} should be equal to ED807 {i_numeration+1} element's {NAMEP}!\n" + 
                f"ED101 val = {ed101_payee.findtext(NAME)}, ED807 val = {ed807_partinfo_entry_for_payee.get(NAMEP)}"
            )
            check_error(ed101_payee.find(BANK).get(BIC), ed807_bic_entry_for_payee.get(BIC), errors_list,
                f"ED101 {payer_payee_pair_counter_numeration} element's payee {BIC} should be equal to ED807 {i_numeration+1} element's {BIC}!\n" + 
                f"ED101 val = {ed101_payee.find(BANK).get(BIC)}, ED807 val = {ed807_bic_entry_for_payee.get(BIC)}"
            )
            check_error(ed101_payee.find(BANK).get(CORRESPACC), ed807_accounts_entry_for_payee.get(ACCOUNT), errors_list,
                f"ED101 {payer_payee_pair_counter_numeration} element's payee {CORRESPACC} should be equal to ED807 {i_numeration+1} element's {ACCOUNT}!\n" + 
                f"ED101 val = {ed101_payee.find(BANK).get(CORRESPACC)}, ED807 val = {ed807_accounts_entry_for_payee.get(ACCOUNT)}"
            )
    
            payer_payee_pair_counter += 1

        assert_error_list(errors_list)