from yapsy.IPlugin import IPlugin
from uatg.instruction_constants import base_reg_file, logic_instructions
from uatg.utils import rvtest_data
from random import randint
from typing import Dict, Any


class uatg_decoder_logical_insts_1(IPlugin):
    """
    This class contains methods to generate and validate the tests for
    logical register register instructions.
    """

    def __init__(self) -> None:
        super().__init__()
        self.isa = 'RV32I'
        self.isa_bit = 'rv32'
        self.isa_load = 'lw'
        self.load_inc = 4
        self.num_rand_var = 100

    def execute(self, _decoder_dict) -> bool:
        # Since logical register instructions exist in all RISCV implementations
        # return True always
        self.isa = _decoder_dict['isa']
        for (i, j, k) in [('rv32', 'lw', 4), ('rv64', 'ld', 8),
                          ('rv128', 'lq', 16)]:
            if i in self.isa.lower():
                self.isa_bit = i
                self.isa_load = j
                self.load_inc = k
        return True

    def generate_asm(self) -> Dict[str, str]:
        """
            Generates the ASM instructions for logical register instructions.
            It creates asm for the following instructions based upon ISA
            and, or, slt, sltu, xor
        """
        asm_data = rvtest_data(bit_width=int(self.isa_bit[2:]), random=True,
                               num_vals=self.num_rand_var, signed=False,
                               align=4)
        reg_file = base_reg_file.copy()
        reg_file.remove('x1')  # Removing X1 register to store Offset address

        # rd, rs1, rs2 iterate through all the 31 register combinations for
        # every instruction in logical_instructions['logic-reg']

        asm_code = '#' * 5 + ' and/or/xor/slt.. reg, reg, reg ' + '#' * 5 + '\n'
        asm_code += '\nla x1, DATA_SEC\n'
        for rd in base_reg_file:
            for rs1 in base_reg_file:
                for rs2 in base_reg_file:
                    assert isinstance(logic_instructions, dict)
                    for inst in logic_instructions['logic-reg']:
                        # asm_code += f'{self.isa_load} {rd}, {randint(0, self.num_rand_var) * self.load_inc}(x1)\n' \
                        #             f'{self.isa_load} {rs1}, {randint(0, self.num_rand_var) * self.load_inc}(x1)\n' \
                        #             f'{self.isa_load} {rs2}, {randint(0, self.num_rand_var) * self.load_inc}(x1)\n'
                        asm_code += f'{inst} {rd}, {rs1}, {rs2}\n'
        return {'asm_code': asm_code, 'asm_data': asm_data}

    def check_log(self, log_file_path, reports_dir) -> bool:
        return False

    def generate_covergroups(self, config_file) -> str:
        sv = ""
        return sv
