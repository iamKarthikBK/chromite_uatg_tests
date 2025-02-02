# This program generates a assembly code which fills the ghr with zeros
from yapsy.IPlugin import IPlugin
from ruamel.yaml import YAML
import uatg.regex_formats as rf
import re
import os
from typing import Dict, List


class uatg_gshare_fa_ghr_zeros_01(IPlugin):
    """
    This class contains methods to
    1. generate asm tests that fills global history register with zeros
    2. checks the log file whether the history register has been filled with 0's
       at least once.

    TODO: Document generate_covergroup
    """

    def __init__(self):
        # initializing variables
        super().__init__()
        self._history_len = 8

    def execute(self, core_yaml, isa_yaml) -> bool:
        # Function to check whether to generate/validate this test or not

        # extract needed values from bpu's parameters
        _bpu_dict = core_yaml['branch_predictor']
        self._history_len = _bpu_dict['history_len']
        _en_bpu = _bpu_dict['instantiate']

        if _en_bpu and self._history_len:
            return True
        else:
            return False

    def generate_asm(self) -> List[Dict[str, str]]:
        """
          the for loop iterates ghr_width + 2 times printing an
          assembly program which contains ghr_width + 2 branches which
          will are NOT TAKEN. This fills the ghr with zeros
        """
        loop_count = self._history_len + 2
        asm = "\n\n## test: gshare_fa_ghr_zeros_01 ##\n\n"
        asm += "  addi t0,x0,1\n"

        for i in range(1, loop_count):
            asm += f"branch_{i}:\n\tbeq t0, x0, branch_{i}\n\taddi t0, t0, 1\n"

        # compile macros for the test
        compile_macros = []

        return [{
            'asm_code': asm,
            'asm_sig': '',
            'compile_macros': compile_macros
        }]

    def check_log(self, log_file_path, reports_dir):
        """
          check if all the ghr values are zero throughout the test
        """
        f = open(log_file_path, "r")
        log_file = f.read()
        f.close()
        test_report = {
            "gshare_fa_ghr_zeros_01_report": {
                'Doc': "ASM should have generated 00000... pattern in the GHR "
                       "Register. This report show's the "
                       "results",
                'expected_GHR_pattern': '',
                'executed_GHR_pattern': [],
                'Execution_Status': ''
            }
        }

        test_report['gshare_fa_ghr_zeros_01_report'][
            'expected_GHR_pattern'] = '0' * self._history_len
        res = None
        # Finding the occurrence of ghr updates
        alloc_newind_pattern_result = re.findall(rf.alloc_newind_pattern,
                                                 log_file)
        ghr_patterns = [
            i[-self._history_len:] for i in alloc_newind_pattern_result
        ]
        # Checking if the required pattern is filled in ghr and deciding status
        for i in ghr_patterns:
            if self._history_len * '0' in i:
                test_report['gshare_fa_ghr_zeros_01_report'][
                    'executed_GHR_pattern'] = i
                test_report['gshare_fa_ghr_zeros_01_report'][
                    'Execution_Status'] = 'Pass'
                res = True
                break
            else:
                res = False
        if not res:
            test_report['gshare_fa_ghr_zeros_01_report'][
                'executed_GHR_pattern'] = ghr_patterns
            test_report['gshare_fa_ghr_zeros_01_report'][
                'Execution_Status'] = 'Fail: expected pattern not found'

        # storing test report at corresponding location
        f = open(
            os.path.join(reports_dir, 'gshare_fa_ghr_zeros_01_report.yaml'),
            'w')
        yaml = YAML()
        yaml.default_flow_style = False
        yaml.dump(test_report, f)
        f.close()
        return res

    def generate_covergroups(self, config_file):
        """
           returns the covergroups for this test
        """
        config = config_file
        rg_ghr = config['branch_predictor']['register']['bpu_rg_ghr']

        sv = f"covergroup bpu_rg_ghr_cg @(posedge CLK); " \
             f"\noption.per_instance=1;\n///coverpoint label can be any name " \
             f"that relates the signal\ncoverpoint_label: coverpoint {rg_ghr}" \
             " {{\n "

        # sv += "\tbins cp1 = {" + f"{self._history_len}" + "{1'b0}};\n"
        # sv += "\tbins cp2 = {" + f"{self._history_len}" + "{1'b1}};\n"
        # sv += "\tbins cp3 = {" + f"{self._history_len // 2}" + "{2'b01}};\n"
        # sv += "\tbins cp4 = {" + f"{self._history_len // 2}" + \
        #       "{2'b10}};\n}\nendgroup\n\n"

        sv += "\tbins bin_allzeros = {'b00000000};\n\tbins bin_allones = {" \
              "'b11111111};\n\tbins bin_altr_10 = {'b10101010};\n\tbins " \
              "bin_altr_01 = {'b01010101};\n}\nendgroup\n\n "

        return sv
