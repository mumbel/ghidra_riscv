#!/usr/bin/env python
"""parse riscv/riscv-opcode file into sleigh"""

arglut = {}
arglut['rd'] = (11,7)
arglut['rs1'] = (19,15)
arglut['rs2'] = (24,20)
arglut['rs3'] = (31,27)
arglut['aqrl'] = (26,25)
arglut['fm'] = (31,28)
arglut['pred'] = (27,24)
arglut['succ'] = (23,20)
arglut['rm'] = (14,12)
arglut['funct3'] = (14,12)
arglut['imm20'] = (31,12)
arglut['jimm20'] = (31,12)
arglut['imm12'] = (31,20)
arglut['imm12hi'] = (31,25)
arglut['bimm12hi'] = (31,25)
arglut['imm12lo'] = (11,7)
arglut['bimm12lo'] = (11,7)
arglut['zimm'] = (19,15)
arglut['shamt'] = (25,20)
arglut['shamtw'] = (24,20)

# for vectors
arglut['vd'] = (11,7)
arglut['vs3'] = (11,7)
arglut['vs1'] = (19,15)
arglut['vs2'] = (24,20)
arglut['vm'] = (25,25)
arglut['wd'] = (26,26)
arglut['amoop'] = (31,27)
arglut['nf'] = (31,29)
arglut['simm5'] = (19,15)
arglut['zimm11'] = (30,20)


def find_display(insn, displays):
    """find display"""
    disp = []
    insn = insn.strip()
    for _ in displays:
        _ = _.strip()
        if _.startswith(insn+" "):
            disp.append(_)
    if not len(disp):
        raise ValueError("NOPE: %s" % insn)
    return disp

def get_display(insn, comment):
    """build display"""
    disp = comment[len(insn):].split('#')[0]
    return disp

def get_pattern(bp):
    """build bit pattern"""
    pattern = ' & '.join(bp)
    return pattern

def parse_line(insn_line, displays):
    """convert line"""
    insn = insn_line.split(' ')
    insn_name = insn[0]

    bit_pattern = []

    comment_lines = find_display(insn_name, displays)

    for _ in insn[1:]:
        _ = _.strip()
        if not len(_):
            continue
        # can be:  arg, arg=value, range=value, bit=value
        # value is decimal or hex
        value = None
        if _.find('=') > -1:
            value = _.split('=')[1]
            if value.find('x') > -1:
                value = int(value, 16)
            else:
                value = int(value, 10)
        arg = _.split('=')[0]
        if arg.find('..') > -1:
            range_hi = int(arg.split('..')[0], 10)
            range_lo = int(arg.split('..')[1], 10)
            arg = (range_lo, range_hi)
        if isinstance(arg, str):
            if arg in arglut.keys():
                pass
            else:
                arg = int(arg, 10)
        # arg is a tuple, int, or str
        # value may be something
        if isinstance(arg, str):
            bp = arg
        elif isinstance(arg, int):
            bp = "op%02d%02d" % (arg, arg)
        else:
            bp = "op%02d%02d" % arg
        if not value is None:
            bp = "%s=0x%x" % (bp, value)
        bit_pattern.append(bp)
    for cmnt in comment_lines:
        d = get_display(insn_name, cmnt)
        p = get_pattern(bit_pattern)
        print "# %s\n# %s\n:%s %s is %s  unimpl\n" % (insn_line, cmnt, insn_name, d, p)

if __name__ == "__main__":

    import sys

    insn_filename = sys.argv[1]
    display_filename = sys.argv[2]
    
    with open(insn_filename, 'r') as f:
        insn_data = f.readlines()
        insn_data.sort()
    with open(display_filename, 'r') as f:
        disp_data = f.readlines()
    
    for _ in insn_data:
        _ = _.strip()
        if not len(_) or _.startswith('#'):
            continue
        parse_line(_, disp_data)
