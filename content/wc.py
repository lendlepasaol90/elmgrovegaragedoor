import json,glob,sys,os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SKIP={'slug','metaTitle','metaDescription','category'}
def wc(o):
  if isinstance(o,str): return len(o.split())
  if isinstance(o,dict): return sum(wc(v) for k,v in o.items() if k not in SKIP)
  if isinstance(o,list): return sum(wc(v) for v in o)
  return 0
for f in ['home.json']+sorted(glob.glob('services/*.json')):
  if os.path.exists(f):
    try: print(f, wc(json.load(open(f))))
    except Exception as e: print(f,'INVALID',e)
