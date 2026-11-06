import sys, struct, re, collections
sys.stdout.reconfigure(encoding='utf-8'); sys.path.insert(0, sys.argv[3])
from linkdata import LinkData
v, p = LinkData(sys.argv[1]), LinkData(sys.argv[2])
jp = re.compile(rb'\xe3[\x81-\x83][\x80-\xbf]')
def kind(d, e):
    t, c, z = struct.unpack(e+'HHI', d[:8])
    if z == 0 and 0 < c < 5000 and 8+4*c <= len(d):
        o = struct.unpack(e+'I', d[8:12])[0]
        if o == 8+4*c or o == ((8+4*c+7)&~7) or o>=8+4*c: return 'TABLE16'
    a, b = struct.unpack(e+'II', d[:8])
    if 0 < a < 1000 and b == 4*(a+1)+0x2c: return 'MSG'
    if 0 < a < 1000 and 8 <= b < len(d): return f'U32HDR(b-4a={b-4*a})'
    return 'OTHER'
groups = collections.defaultdict(list)
for i in range(112, len(v)):
    dv = v.read(i)
    if not jp.search(dv): continue
    dp = p.read(i+2)
    groups[(kind(dv,'<'), kind(dp,'>'))].append(i)
for k, ids in sorted(groups.items(), key=lambda x:-len(x[1])):
    print(k, len(ids), ids[:12], '...' if len(ids)>12 else '')
