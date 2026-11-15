#!/usr/bin/env python3
"""
Samuda Growth Hub - build data.json from the Excel files.

Usage:
    python build_data.py                      # reads every .xlsx in this folder, writes data.json here
    python build_data.py file1.xlsx file2.xlsx file3.xlsx [out.json]

The script finds what it needs by SHEET NAME / COLUMN NAMES, so the file names do not matter:
    SALES_ORDER, DELIVERY_ORDER, PRIMARY_SALES_COLLECTION   (the dump file)
    SKU_MASTER                                              (the product master file)
    customer master = a sheet called CUSTOMER_MASTER, or every sheet that has the columns
                      DISTRIBUTOR_CODE and REGION_BASE (e.g. the Adhesive / Corporate / Thinner sheets)
The old single workbook (Samuda_Growth_Dashboard_v5.xlsx) still works too.

data.json holds monthly totals per customer and product (no order lines, no prices),
plus the open order lines for the Pending delivery view. The web page does all the
sums itself, so every view can be filtered by Year, Month, Business Unit, Region,
Territory, Distributor and Product Category.

Rules:
  Order      = SALES_ORDER "Total Amount" by Order Date (all statuses)
  Delivery   = DELIVERY_ORDER "Delivery Amount" by Delivery Date
  Collection = PRIMARY_SALES_COLLECTION "Collection Amount" by Collection Date (all collection types)
  Product    -> SKU_MASTER (Product Code = ERP_SKU_CODE): segment, SKU group, category, TON factor
  Customer   -> customer master (Customer Code = DISTRIBUTOR_CODE): BU, region, territory (ASM_BASE), channel

Needs: Python 3.9+, pandas, openpyxl   (pip install pandas openpyxl)
"""
import json, sys, os, glob, datetime as dt
import pandas as pd
import openpyxl

THRESHOLD = 0.8                 # Settings: Top contribution threshold
RUBBER_KEY = 'Rubber Adhesive'  # Settings: Rubber-adhesive keyword (matched in SKU group)
AMT_UNIT = 10                   # amounts are stored in units of 10 Taka (whole numbers)


def s(x):
    return '' if x is None or (isinstance(x, float) and pd.isna(x)) else str(x).strip()


DATA_SHEETS = ['SALES_ORDER', 'DELIVERY_ORDER', 'PRIMARY_SALES_COLLECTION']
NEED = {'SALES_ORDER': ['Order Date', 'Order Number', 'Customer Code', 'Product Code', 'Quantity', 'Total Amount', 'Sale Type', 'Status', 'Invoice Status', 'Unit Price', 'Discount%'],
        'DELIVERY_ORDER': ['Delivery Date', 'Sale Order', 'Customer Code', 'Product Code', 'Delivery Quantity', 'Delivery Amount', 'Sales Type'],
        'PRIMARY_SALES_COLLECTION': ['COLLECTION_DATE', 'CUSTOMER_CODE', 'CUSTOMER_NAME', 'COLLECTION_AMOUNT'],
        'SKU_MASTER': ['ERP_SKU_CODE', 'ERP_SKU_NAME', 'SKU_SEGMENT', 'BU_CATEGORY', 'SKU_CATEGORY', 'SKU_GROUP', 'TON_COV_FACTOR'],
        'CUSTOMER_MASTER': ['DISTRIBUTOR_CODE', 'DISTRIBUTOR_NAME', 'BU', 'REGION_BASE', 'ASM_BASE', 'DISTRIBUTION_CHANNEL']}


def load_sources(paths):
    """Find the five tables in the given workbooks (by sheet name / header) and read them."""
    books = []
    for p in paths:
        try:
            wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        except Exception as e:
            print('  skipped %s (%s)' % (os.path.basename(p), e))
            continue
        heads = {}
        for ws in wb.worksheets:
            row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), ())
            heads[ws.title] = [s(c) for c in (row or ())]
        wb.close()
        books.append({'path': p, 'heads': heads, 'dump': any(n in heads for n in DATA_SHEETS), 'mtime': os.path.getmtime(p)})
    if not books:
        sys.exit('No Excel file found. Put the .xlsx files in the same folder as build_data.py.')

    def best(cands, master=False):
        # masters: prefer a dedicated master file over the big dump/workbook; then the newest file
        return sorted(cands, key=lambda b: ((b['dump'] if master else False), -b['mtime'], b['path']))[0]

    plan = {}
    for name in DATA_SHEETS + ['SKU_MASTER']:
        c = [b for b in books if name in b['heads']]
        if c:
            plan[name] = (best(c, name == 'SKU_MASTER'), [name])
    c = [b for b in books if 'CUSTOMER_MASTER' in b['heads']]
    loose = [b for b in books if any({'DISTRIBUTOR_CODE', 'REGION_BASE'} <= set(h) for n, h in b['heads'].items() if n != 'CUSTOMER_MASTER')]
    cand = [(b, ['CUSTOMER_MASTER']) for b in c] + [(b, [n for n, h in b['heads'].items() if {'DISTRIBUTOR_CODE', 'REGION_BASE'} <= set(h)]) for b in loose if b not in c]
    if cand:
        pick = best([x[0] for x in cand], True)
        plan['CUSTOMER_MASTER'] = [x for x in cand if x[0] is pick][0]
    missing = [n for n in DATA_SHEETS + ['SKU_MASTER', 'CUSTOMER_MASTER'] if n not in plan]
    if missing:
        found = '; '.join('%s: %s' % (os.path.basename(b['path']), ', '.join(b['heads'])) for b in books)
        sys.exit('Cannot find: %s.\nSheets found -> %s' % (', '.join(missing), found))

    sh, cache = {}, {}
    for name, (b, sheets) in plan.items():
        print('  %-26s <- %s [%s]' % (name, os.path.basename(b['path']), ', '.join(sheets)))
        for sn in sheets:
            if (b['path'], sn) not in cache:
                want = [x for x in sheets if (b['path'], x) not in cache]
                got = pd.read_excel(b['path'], engine='openpyxl', sheet_name=[x for n2, (b2, s2) in plan.items() if b2 is b for x in s2])
                for k, v in got.items():
                    cache[(b['path'], k)] = v
        df = pd.concat([cache[(b['path'], sn)] for sn in sheets], ignore_index=True) if len(sheets) > 1 else cache[(b['path'], sheets[0])]
        df.columns = [s(c) for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()]
        lack = [c for c in NEED[name] if c not in df.columns]
        if lack:
            sys.exit('%s in %s is missing column(s): %s' % (name, os.path.basename(b['path']), ', '.join(lack)))
        sh[name] = df
    return sh


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    args = sys.argv[1:]
    out = os.path.join(here, 'data.json')
    if args and args[-1].lower().endswith('.json'):
        out = args.pop()
    paths = args or sorted(p for p in glob.glob(os.path.join(here, '*.xls[xm]')) if not os.path.basename(p).startswith('~$'))
    print('Reading %d Excel file(s) (about 30 seconds)...' % len(paths))
    sh = load_sources(paths)

    # ---------- masters ----------
    skm = sh['SKU_MASTER']
    sku_idx, skus = {}, []
    for _, r in skm.iterrows():
        code = s(r['ERP_SKU_CODE'])
        if not code or code in sku_idx:
            continue
        seg = s(r['SKU_SEGMENT'])
        seg = s(r['BU_CATEGORY']) if seg == 'Trading' else (seg or '(Unassigned)')
        name = s(r['ERP_SKU_NAME']) or code
        if name.startswith('['):
            name = name.split(']', 1)[-1].strip() or name
        f = pd.to_numeric(r['TON_COV_FACTOR'], errors='coerce')
        sku_idx[code] = len(skus)
        skus.append([code, name, seg, s(r['SKU_GROUP']) or '(Ungrouped)', s(r['SKU_CATEGORY']) or '(Unassigned)', 0 if pd.isna(f) else float(f)])

    cum = sh['CUSTOMER_MASTER']
    cust_idx, custs = {}, []
    for _, r in cum.iterrows():
        code = s(r['DISTRIBUTOR_CODE'])
        if not code or code in cust_idx:
            continue
        cust_idx[code] = len(custs)
        custs.append([code, s(r['DISTRIBUTOR_NAME']) or code, s(r['BU']) or '(Unassigned)', s(r['REGION_BASE']) or '(Unassigned)',
                      s(r['ASM_BASE']) or '(Unassigned)', s(r['DISTRIBUTION_CHANNEL']) or '(Unassigned)', 1])

    def cid(code, name=''):
        code = s(code)
        if code not in cust_idx:          # not in CUSTOMER_MASTER: kept, flagged with in-master = 0
            cust_idx[code] = len(custs)
            custs.append([code, s(name) or code, '', '', '', '', 0])
        return cust_idx[code]

    def sid(code, name=''):
        code = s(code)
        if code not in sku_idx:           # not in SKU_MASTER: counted in totals only
            sku_idx[code] = len(skus)
            skus.append([code, s(name) or code, '', '', '', 0])
        return sku_idx[code]

    # ---------- facts ----------
    def facts(df, date, amt, cust, cname, sku=None, sname=None, qty=None, free=None):
        d = pd.DataFrame({'date': pd.to_datetime(df[date], errors='coerce'), 'amt': pd.to_numeric(df[amt], errors='coerce').fillna(0)})
        d['c'] = [cid(a, b) for a, b in zip(df[cust], df[cname])]
        if sku:
            d['s'] = [sid(a, b) for a, b in zip(df[sku], df[sname])]
            fac = pd.Series([skus[i][5] for i in d['s']], index=d.index)
            q = pd.to_numeric(df[qty], errors='coerce').fillna(0)
            d['t'] = (q * fac * 1000).where(~df[free].eq('Free Product'), 0)
        d = d.dropna(subset=['date'])
        meta = {'first': d.date.min().strftime('%Y-%m-%d'), 'lastAny': d.date.max().strftime('%Y-%m-%d'),
                'lastAmt': d[d.amt > 0].date.max().strftime('%Y-%m-%d') if (d.amt > 0).any() else None}
        d['ym'] = (d.date.dt.year - 2000) * 12 + d.date.dt.month - 1
        keys = ['ym', 'c'] + (['s'] if sku else [])
        g = d.groupby(keys, as_index=False).agg({'amt': 'sum', **({'t': 'sum'} if sku else {})})
        g = g[(g.amt != 0) | ((g['t'] != 0) if sku else False)]
        cols = {'ym': g.ym.astype(int).tolist(), 'c': g.c.astype(int).tolist(), 'a': (g.amt / AMT_UNIT).round().astype(int).tolist()}
        if sku:
            cols['s'] = g.s.astype(int).tolist()
            cols['t'] = g.t.round().astype(int).tolist()
        return cols, meta

    so, do, co = sh['SALES_ORDER'], sh['DELIVERY_ORDER'], sh['PRIMARY_SALES_COLLECTION']
    O, mO = facts(so, 'Order Date', 'Total Amount', 'Customer Code', 'Customer Name', 'Product Code', 'Product Name', 'Quantity', 'Sale Type')
    D, mD = facts(do, 'Delivery Date', 'Delivery Amount', 'Customer Code', 'Customer Name', 'Product Code', 'Product Name', 'Delivery Quantity', 'Sales Type')
    C, mC = facts(co, 'COLLECTION_DATE', 'COLLECTION_AMOUNT', 'CUSTOMER_CODE', 'CUSTOMER_NAME')

    # ---------- pending delivery (open order lines) ----------
    od = pd.to_datetime(so['Order Date'], errors='coerce')
    asof = od.max()
    p = so[(od.dt.year == asof.year) & so['Status'].eq('Approved') & so['Invoice Status'].eq('To Invoice') & ~so['Sale Type'].eq('Free Product')].copy()
    p['date'] = od
    p['q'] = pd.to_numeric(p['Quantity'], errors='coerce').fillna(0)
    p['pr'] = pd.to_numeric(p['Unit Price'], errors='coerce').fillna(0)
    p['ds'] = pd.to_numeric(p['Discount%'], errors='coerce').fillna(0)
    p['ps'] = p['Product Code'].map(s)
    g = p.groupby(['Order Number', 'ps']).agg(q=('q', 'sum'), pr=('pr', 'mean'), ds=('ds', 'mean'), date=('date', 'min'),
                                                cust=('Customer Code', 'first'), cn=('Customer Name', 'first'), pn=('Product Name', 'first')).reset_index()
    dl = do[~do['Sales Type'].eq('Free Product')].copy()
    dl['ps'] = dl['Product Code'].map(s)
    dq = dl.groupby(['Sale Order', 'ps'])['Delivery Quantity'].sum()
    g['dq'] = [dq.get((a, b), 0) for a, b in zip(g['Order Number'], g['ps'])]
    g['pq'] = (g.q - g.dq).clip(lower=0)
    g['pv'] = g.pq * g.pr * (1 - g.ds / 100)
    g = g[g.pv > 0]
    orders = {}
    pend = []
    for _, r in g.iterrows():
        si = sid(r.ps, r.pn)
        pend.append([cid(r.cust, r.cn), si, orders.setdefault(r['Order Number'], len(orders)), int((asof - r.date).days),
                     int(round(r.pv / AMT_UNIT)), int(round(r.pq * skus[si][5] * 1000))])

    data = {'v': 5, 'built': dt.datetime.now().strftime('%d-%b-%Y %H:%M'), 'unit': AMT_UNIT,
            'settings': {'threshold': THRESHOLD, 'rubber': RUBBER_KEY},
            'meta': {'order': mO, 'delivery': mD, 'collection': mC, 'pendingAsOf': asof.strftime('%Y-%m-%d')},
            'cust': custs, 'sku': [x[:5] for x in skus],
            'O': O, 'D': D, 'C': C, 'P': pend}
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print('Wrote %s  (%.1f MB) - built %s' % (out, os.path.getsize(out) / 1e6, data['built']))


if __name__ == '__main__':
    main()
