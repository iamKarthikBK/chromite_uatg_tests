from yapsy.IPlugin import IPlugin
from typing import Dict, List, Union


class uatg_mbox_signed_mul(IPlugin):
    """
    This class contains methods to generate and validate the signed 
    multiplication operation using mulh instruction
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
        if 'M' in self.isa or 'Zmmul' in self.isa:
            return True
        else:
            return False

    def generate_asm(self) -> List[Dict[str, Union[str, list]]]:
        """
            It creates asm for signed multiplication using mulh instruction 
        """
        test_dict = []

        asm_code = '#' * 5 + ' mulh/mul reg, reg, reg ' + '#' * 5 + '\n'

        # initial register to use as signature pointer
        swreg = 'x31'

        # registers that are used as rs1, rs2 and rd
        rs1 = 'x3'
        rs2 = 'x4'
        rd = 'x5'
        rd1 = 'x6'
        # initialize swreg to point to signature_start label
        asm_code += f'RVTEST_SIGBASE({swreg}, signature_start)\n'

        # initial offset to with respect to signature label
        offset = 0

        # variable to hold the total number of signature bytes to be used.
        sig_bytes = 0

        rs1_val, rs2_val = None, None
        # data to populate rs1 and rs2 registers
        if 'RV32' in self.isa:
            rs1_val = '0xfffff63c'  # negative
            rs2_val = '0xffac1df3'  # negative
        elif 'RV64' in self.isa:
            rs1_val = '0xfdb97531eca86420'
            rs2_val = '0xfeca86420db97531'
 
        # perform the  required assembly operation
        asm_code += f'\n#operation: mulh, rs1={rs1}, rs2={rs2}, rd={rd}\n'

        asm_code += f'TEST_RR_OP(mulh, {rd}, {rs1}, {rs2}, 0, {rs1_val}, ' \
                    f'{rs2_val}, {swreg}, {offset}, x0)\n'

        # increment offset by the amount of bytes updated in
        # signature by each test-macro.
        offset = offset + self.offset_inc

        # keep track of the total number of signature bytes used
        # so far.
        sig_bytes = sig_bytes + self.offset_inc

        asm_code += f'#operation: mul, rs1={rs1}, rs2={rs2}, rd={rd}\n'

        asm_code += f'TEST_RR_OP(mul, {rd1}, {rs1}, {rs2}, 0, {rs1_val}, ' \
                    f'{rs2_val}, {swreg}, {offset}, x0)\n'

        # asm code to populate the signature region
        sig_code = 'signature_start:\n'
        sig_code += ' .fill {0},4,0xdeadbeef\n'.format(int(sig_bytes / 4))

        # compile macros for the test
        compile_macros = []

        # return asm_code and sig_code
        test_dict.append({
            'asm_code': asm_code,
            'asm_data': '',
            'asm_sig': sig_code,
            'compile_macros': compile_macros
        })
        return test_dict

    def check_log(self, log_file_path, reports_dir) -> bool:
        return False

    def generate_covergroups(self, config_file) -> str:
        sv = ""
        return sv
