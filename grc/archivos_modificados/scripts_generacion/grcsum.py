import sys, yaml
for p in sys.argv[1:]:
    d = yaml.safe_load(open(p, encoding='utf-8', errors='replace'))
    o = d['options']['parameters']
    print(f"\n######## {p}\n title={o.get('title')!r} id={o.get('id')} gen={o.get('generate_options')}\n desc={o.get('description')!r}")
    vars_, blks = [], []
    for b in d.get('blocks', []):
        st = b.get('states',{}).get('state')
        if b['id'].startswith('variable') or b['id'] in ('parameter',):
            v = b['parameters'].get('value', b['parameters'].get('start', b['parameters'].get('default','')))
            vars_.append(f"{b['name']}={v}" + ("" if st=='enabled' else f"[{st}]"))
        else:
            extra = ''
            if b['id'] == 'epy_block':
                src = b['parameters'].get('_source_code','')
                extra = ' name=' + (src.split("name='")[1].split("'")[0] if "name='" in src else '?')
                for k,v in b['parameters'].items():
                    if k not in ('_source_code','comment','affinity','alias','maxoutbuf','minoutbuf','_io_cache'): extra += f" {k}={v}"
            blks.append(f"{b['name']}:{b['id']}{'' if st=='enabled' else '['+str(st)+']'}{extra}")
    print(" VARS:", "; ".join(vars_))
    print(" BLOCKS:"); [print("   ", x) for x in blks]
    print(" CONN:", "; ".join(f"{c[0]}:{c[1]}->{c[2]}:{c[3]}" for c in d.get('connections', [])))
