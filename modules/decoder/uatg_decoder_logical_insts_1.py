from yapsy.IPlugin import IPlugin
from uatg.instruction_constants import base_reg_file, logic_instructions
from uatg.utils import rvtest_data
from typing import Dict
import random


class uatg_decoder_logical_insts_1(IPlugin):
    """
    This class contains methods to generate and validate the tests for
    logical register register instructions.
    """

    def __init__(self) -> None:
        super().__init__()
        self.isa = 'RV32I'
        self.isa_bit = 'rv32'
        self.offset_inc = 4
        self.xlen = 32
        self.num_rand_var = 100

    def execute(self, core_yaml, isa_yaml) -> bool:
        self.isa = isa_yaml['hart0']['ISA']
        if 'RV32' in self.isa:
            self.isa_bit = 'rv32'
            self.xlen = 32
            self.offset_inc = 4
        else:
            self.isa_bit = 'rv64'
            self.xlen = 64
            self.offset_inc = 8
        return True

    def generate_asm(self):
        """
            Generates the ASM instructions for logical register instructions.
            It creates asm for the following instructions based upon ISA
            and, or, slt, sltu, xor
        """
        asm_data = rvtest_data(bit_width=int(self.isa_bit[2:]),
                               random=True,
                               num_vals=self.num_rand_var,
                               signed=False,
                               align=4)
        reg_file = base_reg_file.copy()
        reg_file.remove('x1')  # Removing X1 register to store Offset address

        # rd, rs1, rs2 iterate through all the 31 register combinations for
        # every instruction in logical_instructions['logic-reg']

        reg_file = base_reg_file.copy()
        test_dict = []
        for inst in logic_instructions['logic-reg']:

            asm_code = '#' * 5 + ' add/sub reg, reg, reg ' + '#' * 5 + '\n'

            # initial register to use as signature pointer
            swreg = 'x31'

            # initialize swreg to point to signature_start label
            asm_code += f'RVTEST_SIGBASE({swreg}, signature_start)\n'

            # initial offset to with respect to signature label
            offset = 0

            # variable to hold the total number of signature bytes to be used.
            sig_bytes = 0

            for rd in reg_file:
                for rs1 in reg_file:
                    for rs2 in reg_file:
                        assert isinstance(logic_instructions, dict)

                        rs1_val = hex(random.getrandbits(self.xlen))
                        rs2_val = hex(random.getrandbits(self.xlen))

                        # if signature register needs to be used for operations
                        # then first choose a new signature pointer and move the
                        # value to it.
                        if swreg in [rd, rs1, rs2]:
                            newswreg = random.choice([
                                x for x in reg_file
                                if x not in [rd, rs1, rs2, 'x0']
                            ])
                            asm_code += f'mv {newswreg}, {swreg}\n'
                            swreg = newswreg

                        # perform the  required assembly operation
                        asm_code += f'\n#operation: {inst}, rs1={rs1}, rs2={rs2}, rd={rd}\n'
                        asm_code += f'TEST_RR_OP({inst}, {rd}, {rs1}, {rs2}, 0, {rs1_val}, {rs2_val}, {swreg}, {offset}, x0)\n'

                        # adjust the offset. reset to 0 if it crosses 2048 and
                        # increment the current signature pointer with the
                        # current offset value
                        if offset + self.offset_inc >= 2048:
                            asm_code += f'addi {swreg}, {swreg}, {offset}\n'
                            offset = 0

                        # increment offset by the amount of bytes updated in
                        # signature by each test-macro.
                        offset = offset + self.offset_inc

                        # keep track of the total number of signature bytes used
                        # so far.
                        sig_bytes = sig_bytes + self.offset_inc

            # asm code to populate the signature region
            sig_code = 'signature_start:\n'
            sig_code += ' .fill {0},4,0xdeadbeef'.format(int(sig_bytes / 4))

            # compile macros for the test
            compile_macros = []

            # return asm_code and sig_code
            test_dict.append({
                'asm_code': asm_code,
                'asm_data': '',
                'asm_sig': sig_code,
                'compile_macros': compile_macros,
                'name_postfix': inst
            })
        return test_dict

    def check_log(self, log_file_path, reports_dir) -> bool:
        return False

    def generate_covergroups(self, config_file) -> str:
        sv = ""
        return sv
