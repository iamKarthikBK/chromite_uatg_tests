from cocotb_coverage.coverage import *
from cocotb_coverage import crv
import cocotb
from enum import Enum, IntEnum, unique, auto

instrs = ['add','sub', 'sll','slt','sltu','xor','srl','sra',
          'or','and', 'addw', 'subw', 'sllw', 'srlw', 'sraw']

xreg = ['x' + str(s) for s in range(32)]

covered = [] # list to store already covered data
irs1_covered = []
irs2_covered = []
ird_covered = []
log = cocotb.logging.getLogger("cocotb.test") #logger instance
class CdtgRandomized(crv.Randomized):

    def __init__(self):
        crv.Randomized.__init__(self)
        self.w = 'x0' #rd
        self.x = 'x0'
        self.y = 'x0'
        self.z = 'add'
        self.add_rand('w', xreg)
        self.add_rand('x', xreg)
        self.add_rand('y', xreg)
        self.add_rand('z', instrs)

        self.rd_not_cov = lambda w, z: (z,w) not in ird_covered
        self.rs1_ne_rs2 = lambda x, y: x != y
        self.rs1_ne_rd  = lambda w, x: w != x
        self.rs2_ne_rd  = lambda w, y: w != y
        self.rs1_not_cov = lambda x, z: (z,x) not in irs1_covered
        self.rs2_not_cov = lambda y, z: (z,y) not in irs2_covered


        # define hard constraint - do not pick items from the "covered" list
        self.add_constraint(lambda w,x,y,z : (z,w,x,y) not in covered)
        #self.add_constraint(lambda x,z : (z, x) not in irs1_covered)
        #self.add_constraint(lambda y,z : (z.name, y) not in irs2_covered)

Mycoverage = coverage_section(
    CoverPoint("top.rs1", xf = lambda obj : obj.x, bins = xreg),
    CoverPoint("top.rs2", xf = lambda obj : obj.y, bins = xreg),
    CoverPoint("top.rd", xf = lambda obj : obj.w, bins = xreg),
    CoverPoint("top.instr", xf = lambda obj : obj.z, bins = instrs),
    CoverCross("top.seq1", items = ["top.instr","top.rs1"]),
    CoverCross("top.seq2", items = ["top.instr","top.rs2"]),
    CoverCross("top.seq3", items = ["top.instr","top.rd"])
)

@Mycoverage
def sample_coverage(obj):
    covered.append((obj.z, obj.w, obj.x, obj.y)) # extend the list with sampled value
    irs1_covered.append((obj.z, obj.x)) # extend the list with sampled value
    irs2_covered.append((obj.z, obj.y)) # extend the list with sampled value
    ird_covered.append((obj.z, obj.w))

obj = CdtgRandomized()
cross_size = coverage_db["top.seq1"].size
cross_coverage = coverage_db["top.seq1"].coverage

#for _ in range(cross_size):
while cross_size != cross_coverage:
    obj.randomize_with(obj.rs1_ne_rs2, obj.rs1_not_cov, obj.rs1_ne_rd)
    sample_coverage(obj)
    cross_coverage = coverage_db["top.seq1"].coverage

print(len(covered))

cross_size = coverage_db["top.seq2"].size
cross_coverage = coverage_db["top.seq2"].coverage
while cross_size != cross_coverage:
    obj.randomize_with(obj.rs2_not_cov, obj.rs2_ne_rd)
    sample_coverage(obj)
    cross_coverage = coverage_db["top.seq2"].coverage

print(len(covered))

cross_size = coverage_db["top.seq3"].size
cross_coverage = coverage_db["top.seq3"].coverage

#for _ in range(cross_size):
while cross_size != cross_coverage:
    obj.randomize_with(obj.rd_not_cov)
    sample_coverage(obj)
    cross_coverage = coverage_db["top.seq3"].coverage

print(len(covered))

with open('insts.txt', 'w') as out: 
    for i in covered:
        out.write(str(i)+'\n')

coverage_db.report_coverage(log.info, bins=True)
coverage_db.export_to_yaml(filename="coverage.yaml")

