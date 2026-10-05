"""Static, trace-derived teaching snapshots. Not screenshots or measured timings."""
from pathlib import Path
import io
import json
import cairosvg
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from .make_slides import REG,BOLD,MONO,wrap
from .graphics import svg_graph

CASES=[
 ('lazy_stale','main','lazy','stale',0,'Why may this record be discarded?','The queue record is obsolete, not the node. B was improved from 6 to 3. Do not scan its outgoing edges again.'),
 ('eager_decrease','main','eager','decrease',0,'Can we repair the entry instead?','One live record per frontier node. A strict decrease changes its priority and the node-to-index map.'),
 ('lazy_goal','main','lazy','finish',0,'When can this route be certified?','The current goal entry was extracted after the stale check. Cost 8 is certified; remaining queue records need not be processed.'),
 ('astar_main','main','astar','finish',0,'Which information changed the order?','With a consistent h, A* reaches the same cost 8 after four expansions. D remains a frontier candidate; fewer expansions is not a universal runtime guarantee.'),
 ('astar_reopen','reopening','astar','reopen',0,'Should A be ignored or processed again?','A was expanded at g=3 and is now reached at g=2. Reopening propagates that improvement. The correct final cost will be 5.'),
 ('closed_failure','reopening','closed_bug','finish',0,'Which assumption did permanent closure require?','DELIBERATELY WRONG: admissibility alone did not justify closing forever. This variant returns 6; reopening returns the optimum 5.')]

def fmt(x):return '∞' if x is None else str(x)

def build(root,data=None):
 root=Path(root);out=root/'fallback';out.mkdir(exist_ok=True)
 if data is None:data=json.loads((root/'web/traces.json').read_text())
 W,H=842,595;c=canvas.Canvas(str(out/'fallback.pdf'),pagesize=(W,H));c.setTitle('Dijkstra and A*: trace-derived fallback snapshots')
 records=[]
 def txt(x,y,text,fs=10,font=REG,color='#17323d'):
  c.setFont(font,fs);c.setFillColor(HexColor(color));c.drawString(x,y,text)
 def para(x,y,text,width,fs=11,font=REG):
  for line in wrap(text,width,fs,font):txt(x,y,line,fs,font);y-=fs*1.35
  return y
 def table(x,top,width,headers,rows,ratios=None,rowheight=17):
  ratios=ratios or [1/len(headers)]*len(headers)
  for i,row in enumerate([headers]+rows):
   yy=top-(i+1)*rowheight;c.setFillColor(HexColor('#e5ede6' if i==0 else '#fffefb' if i%2 else '#f0f3ef'));c.rect(x,yy,width,rowheight,fill=1,stroke=0)
   xx=x
   for val,r in zip(row,ratios):txt(xx+6,yy+5,str(val),8.6,BOLD if i==0 else REG);xx+=width*r
 for page,(name,key,algorithm,kind,occ,title,prompt) in enumerate(CASES,1):
  t=data[key][algorithm];events=[e for e in t['events'] if e['kind']==kind];e=events[occ]
  c.setFillColor(HexColor('#f3f1eb'));c.rect(0,0,W,H,fill=1,stroke=0)
  txt(32,565,'FALLBACK / '+algorithm.upper().replace('_',' '),10,BOLD,'#087e79');txt(32,537,title,21,BOLD)
  txt(32,516,t['name']+'  ·  Actual Python state after the highlighted operation',9)
  svg=svg_graph(t['case'],show_h=algorithm in ('astar','closed_bug'),state=e)
  png=cairosvg.svg2png(bytestring=svg.encode(),output_width=1100,output_height=636)
  c.drawImage(ImageReader(io.BytesIO(png)),28,246,445,257,mask='auto')
  if algorithm in ('astar','closed_bug'):
   nodes=[[n,fmt(e['dist'].get(n)),str(t['case']['h'][n]),e['parent'].get(n,'—')] for n in t['case']['graph']]
   table(495,498,315,['Node','g','h','Parent'],nodes,[.22,.25,.23,.30])
  else:
   nodes=[[n,fmt(e['dist'].get(n)),e['parent'].get(n,'—')] for n in t['case']['graph']]
   table(495,498,315,['Node','g','Parent'],nodes,[.30,.35,.35])
  q=sorted(e['queue'],key=lambda q:(q['priority'],q['ticket']))
  txt(495,294,'Frontier in priority order (not heap storage)',9,BOLD)
  rows=[[r['node']+(' ×' if r['stale'] else ''),str(r['priority']),str(r['g'])] for r in q]
  table(495,286,315,['Node','Priority','Queued g'],rows or [['empty','—','—']],[.30,.35,.35],rowheight=16)
  para(32,223,prompt,426,11)
  st=e['stats'];txt(32,145,'Expansions: '+str(st.get('expansions',0))+'    Stale skips: '+str(st.get('stale_pops',0))+'    Re-expansions: '+str(st.get('reexpansions',0))+'    Peak queue: '+str(st.get('peak_queue',0)),10,BOLD)
  c.setFillColor(HexColor('#e0eae2'));c.roundRect(32,62,778,65,6,stroke=0,fill=1)
  txt(44,110,t['source_file']+' / function-relative line '+str(e['line'])+' (just executed)',9,BOLD)
  para(44,91,e['code'],752,9.5,MONO)
  txt(32,38,'Gold = current   Green = frontier   Blue = finalized (Dijkstra) / expanded (A*, may reopen)',8)
  txt(32,23,'Static snapshots generated from the Python traces; animation playback speed is not runtime.',7.5)
  txt(790,23,str(page),9,BOLD)
  records.append(dict(name=name,case=key,algorithm=algorithm,event_index=e['index'],relative_line=e['line'],kind=e['kind']))
  c.showPage()
 c.save()
 import fitz
 d=fitz.open(out/'fallback.pdf')
 for pg,record in zip(d,records):pg.get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(out/(record['name']+'.png'))
 (out/'snapshot_manifest.json').write_text(json.dumps(records,indent=2)+'\n')
 (out/'README.md').write_text('''# Offline fallback

`fallback.pdf` and the six PNG files are static state panels generated from actual Python execution traces. They are not separately simulated algorithm states or browser screenshots. The manifest identifies the exact trace event.

Keep the PDF open before teaching. Use the panels for stale records, decrease-key, correct target extraction, A* on the main graph, reopening, and the deliberately wrong closed-set policy. The final result in the reopening prompt is a discussion/solution cue, not the state's current target label.

Rebuild with `python tools/build_all.py`. No browser or network is needed for this fallback.
''')
 return records

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
