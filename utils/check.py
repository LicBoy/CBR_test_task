# Some utils to store all assert fail texts for multiple checking

def check_error(expected, actual, result_list: list, error_msg: str, dont_continue = False):
    if expected != actual:
        result_list.append(error_msg)
        if dont_continue:
            assert_error_list(result_list)

def assert_error_list(errors_list: list):
    assert len(errors_list) == 0, "\n".join(errors_list)