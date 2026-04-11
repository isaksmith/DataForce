import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="MAGI Dashboard", layout="wide")

branches = pd.read_csv("Hack The Plains 2026 Datasets/branches.csv")

state_points = [
  {"state": "KS", "x": 470, "y": 255, "cityCount": 0, "branchCount": 0, "cities": []},
  {"state": "OK", "x": 455, "y": 315, "cityCount": 0, "branchCount": 0, "cities": []},
  {"state": "NE", "x": 440, "y": 205, "cityCount": 0, "branchCount": 0, "cities": []},
  {"state": "MO", "x": 525, "y": 265, "cityCount": 0, "branchCount": 0, "cities": []},
]

branch_summary = (
  branches.groupby("branch_state")
  .agg(branchCount=("branch_code", "count"), cityCount=("branch_city", "nunique"))
  .reset_index()
)
city_summary = (
  branches.groupby(["branch_state", "branch_city"]) 
  .size()
  .reset_index(name="branches")
)

state_lookup = {item["state"]: item for item in state_points}
for row in branch_summary.itertuples():
  if row.branch_state in state_lookup:
    state_lookup[row.branch_state]["branchCount"] = int(row.branchCount)
    state_lookup[row.branch_state]["cityCount"] = int(row.cityCount)
    state_lookup[row.branch_state]["cities"] = city_summary[city_summary["branch_state"] == row.branch_state][
      ["branch_city", "branches"]
    ].to_dict(orient="records")

map_data_json = json.dumps(state_points)

html = """
<script src="https://cdn.tailwindcss.com"></script>
<div id="root"></div>
<script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
<script>
  const e = React.createElement;
  const mapData = __MAP_DATA__;

  const DataNode = ({ title, children, className = '', titleClass = '' }) =>
    e('div', {
      className: `border border-amber-400 shadow-[0_0_0_1px_#f59e0b] p-3 ${className}`
    }, [
      e('div', { className: `text-[11px] tracking-[0.35em] font-bold mb-3 ${titleClass}` }, title),
      e('div', { className: 'space-y-2' }, children)
    ]);

  const MetricLine = ({ label, value, valueClass = '' }) =>
    e('div', { className: 'flex items-end justify-between gap-4 border-b-2 border-current pb-1' }, [
      e('span', { className: 'text-[11px] uppercase tracking-[0.2em] font-bold' }, label),
      e('span', { className: `font-mono text-lg font-bold ${valueClass}` }, value)
    ]);

  const TerminalNode = ({ title, children, accent = 'text-amber-300' }) =>
    e('div', {
      className: `bg-black ${accent} border border-amber-500 p-4 relative`
    }, [
      e('div', { className: 'absolute inset-0 opacity-10 pointer-events-none', style: { backgroundImage: 'linear-gradient(to right, rgba(251,191,36,0.14) 1px, transparent 1px), linear-gradient(to bottom, rgba(251,191,36,0.14) 1px, transparent 1px)', backgroundSize: '12px 12px' } }),
      e('div', { className: 'relative z-10' }, [
        e('div', { className: 'text-[11px] tracking-[0.35em] font-bold mb-3' }, title),
        e('div', { className: 'space-y-2 font-mono' }, children)
      ])
    ]);

  const USMap = () => {
    const [hovered, setHovered] = React.useState(mapData[0] || null);

    return e('div', { className: 'grid grid-cols-5 gap-4 h-full' }, [
      e('div', { className: 'col-span-3 bg-[#05070b] border border-amber-500 p-3 relative min-h-[520px]' }, [
        e('div', { className: 'text-[11px] tracking-[0.35em] text-amber-300 font-bold mb-2' }, 'US GEO NODE / BRANCH PRESENCE'),
        e('svg', { viewBox: '0 0 800 500', className: 'w-full h-[460px] bg-[#020409]' }, [
          e('rect', { x: 0, y: 0, width: 800, height: 500, fill: '#020409' }),
          e('path', {
            d: 'M90,120 L180,90 L255,104 L330,95 L390,110 L470,95 L570,110 L675,155 L705,205 L680,280 L620,350 L520,385 L430,390 L325,405 L245,380 L165,350 L110,300 L86,230 Z',
            fill: '#0b1220', stroke: '#fbbf24', strokeWidth: 4
          }),
          mapData.map((point, idx) => e('g', {
            key: point.state,
            onMouseEnter: () => setHovered(point),
            style: { cursor: 'pointer' }
          }, [
            e('circle', {
              cx: point.x,
              cy: point.y,
              r: 16 + Math.max(point.branchCount * 1.4, 10),
              fill: idx % 2 === 0 ? '#f59e0b' : '#22d3ee',
              fillOpacity: 0.25,
              stroke: idx % 2 === 0 ? '#fbbf24' : '#67e8f9',
              strokeWidth: 3
            }),
            e('circle', {
              cx: point.x,
              cy: point.y,
              r: 5,
              fill: '#fef3c7'
            }),
            e('text', {
              x: point.x,
              y: point.y - 28,
              textAnchor: 'middle',
              fill: '#fef3c7',
              fontSize: 18,
              fontFamily: 'monospace',
              fontWeight: 700
            }, point.state)
          ]))
        ])
      ]),
      e('div', { className: 'col-span-2 bg-black text-amber-300 border border-amber-500 p-4 font-mono' }, [
        e('div', { className: 'text-[11px] tracking-[0.35em] font-bold mb-4' }, 'HOVER DETAIL / STATE TERMINAL'),
        hovered ? e('div', { className: 'space-y-3' }, [
          e('div', { className: 'text-3xl font-bold' }, hovered.state),
          e('div', { className: 'grid grid-cols-2 gap-2 text-sm' }, [
            e('div', { className: 'border border-amber-600 p-2' }, [e('div', { className: 'text-[10px]' }, 'BRANCHES'), e('div', { className: 'text-xl font-bold' }, String(hovered.branchCount))]),
            e('div', { className: 'border border-amber-600 p-2' }, [e('div', { className: 'text-[10px]' }, 'CITIES'), e('div', { className: 'text-xl font-bold' }, String(hovered.cityCount))])
          ]),
          e('div', { className: 'border border-amber-600 p-3' }, [
            e('div', { className: 'text-[10px] tracking-[0.25em] mb-2' }, 'CITY BREAKDOWN'),
            ...hovered.cities.map(city => e('div', { className: 'flex justify-between border-b border-amber-800 py-1 text-sm' }, [
              e('span', null, city.branch_city),
              e('span', null, String(city.branches))
            ]))
          ])
        ]) : null
      ])
    ]);
  };

  const Dashboard = () =>
    e('div', { className: 'min-h-screen bg-[#0f1116] text-amber-300 p-4 font-mono' }, [
      e('div', { className: 'border border-amber-500 bg-black px-4 py-3 mb-4' }, [
        e('div', { className: 'flex items-center justify-between gap-4' }, [
          e('div', { className: 'text-3xl font-bold tracking-[0.25em] text-amber-300' }, 'DATAFORCE EXPLORER // TERMINAL'),
          e('div', { className: 'text-sm text-amber-200' }, 'SMARTRESOLVE / NATIONAL COMMAND VIEW')
        ])
      ]),
      e('div', { className: 'grid grid-cols-12 gap-4' }, [
        e('div', { className: 'col-span-3 flex flex-col gap-4' }, [
          e(TerminalNode, { title: 'LIVE TELEMETRY', accent: 'text-cyan-300' }, [
            e(MetricLine, { label: 'Total Sessions', value: '2,000,000' }),
            e(MetricLine, { label: 'Failed Transactions', value: '4.8%' })
          ]),
          e(TerminalNode, { title: 'ERROR TRACKING', accent: 'text-cyan-300' }, [
            e(MetricLine, { label: 'ERR_AUTH', value: '15K' }),
            e(MetricLine, { label: 'ERR_TIMEOUT', value: '8K' }),
            e(MetricLine, { label: 'ERR_DEPOSIT', value: '5K' })
          ]),
          e(TerminalNode, { title: 'COST PER FEATURE', accent: 'text-cyan-300' }, [
            e('div', { className: 'space-y-3' }, [
              e('div', null, [
                e('div', { className: 'flex justify-between text-xs mb-1' }, [e('span', null, 'Mobile Deposit'), e('span', null, '$0.76')]),
                e('div', { className: 'h-3 bg-amber-950 border border-amber-400' }, e('div', { className: 'h-full bg-amber-300 w-[78%]' }))
              ]),
              e('div', null, [
                e('div', { className: 'flex justify-between text-xs mb-1' }, [e('span', null, 'Web Portal'), e('span', null, '$0.44')]),
                e('div', { className: 'h-3 bg-amber-950 border border-amber-400' }, e('div', { className: 'h-full bg-cyan-300 w-[46%]' }))
              ])
            ])
          ])
        ]),
        e('div', { className: 'col-span-6 flex flex-col gap-4' }, [
          e('div', { className: 'bg-black border border-amber-500 p-4' }, [
            e('div', { className: 'grid grid-cols-3 gap-4 mb-4' }, [
              e(DataNode, { title: 'DEMOGRAPHICS', className: 'bg-[#111827] text-amber-300', titleClass: 'text-amber-200' }, [e(MetricLine, { label: 'Active Profiles', value: '355,000' })]),
              e(DataNode, { title: 'SESSION LOGS', className: 'bg-[#111827] text-amber-300', titleClass: 'text-amber-200' }, [e(MetricLine, { label: 'Failed Pathways', value: '96,000' })]),
              e(DataNode, { title: 'SUPPORT ALERTS', className: 'bg-[#111827] text-amber-300', titleClass: 'text-amber-200' }, [e(MetricLine, { label: 'Live Tickets', value: '65,000' })])
            ]),
            e('div', { className: 'border border-red-500 bg-[#220808] p-6 text-center' }, [
              e('div', { className: 'text-sm tracking-[0.35em] mb-3 text-red-300 font-bold' }, 'TOTAL FRICTION COST'),
              e('div', { className: 'text-6xl font-bold text-red-400' }, '$12,450.00'),
              e('div', { className: 'mt-4 border border-amber-500 bg-black px-4 py-2 text-lg tracking-[0.25em] text-amber-300 animate-pulse' }, 'SYSTEM INTERVENTION: REQUIRED')
            ])
          ]),
          e(USMap)
        ]),
        e('div', { className: 'col-span-3 flex flex-col gap-4' }, [
          e(DataNode, { title: 'CUSTOMER DEMOGRAPHICS', className: 'bg-black text-amber-300', titleClass: 'text-amber-300' }, [
            e(MetricLine, { label: 'Active Profiles', value: '355,000', valueClass: 'text-amber-300' })
          ]),
          e(DataNode, { title: 'SUPPORT SATURATION', className: 'bg-black text-amber-300', titleClass: 'text-amber-300' }, [
            e(MetricLine, { label: 'Live Tickets', value: '65,000', valueClass: 'text-amber-300' }),
            e(MetricLine, { label: 'Agent Load', value: '92%', valueClass: 'text-amber-300' })
          ]),
          e(DataNode, { title: 'TARGET VETO', className: 'bg-black text-amber-300', titleClass: 'text-amber-300' }, [
            e('div', { className: 'border-2 border-red-500 bg-red-950 text-red-300 p-4 text-center text-2xl font-bold tracking-[0.2em] uppercase animate-pulse' }, 'Churn Risk Detected: High')
          ]),
          e(DataNode, { title: 'GEO WATCHLIST', className: 'bg-black text-cyan-300', titleClass: 'text-cyan-300' }, [
            e(MetricLine, { label: 'Kansas Nodes', value: '24', valueClass: 'text-cyan-300' }),
            e(MetricLine, { label: 'Oklahoma Nodes', value: '5', valueClass: 'text-cyan-300' }),
            e(MetricLine, { label: 'Nebraska Nodes', value: '4', valueClass: 'text-cyan-300' }),
            e(MetricLine, { label: 'Missouri Nodes', value: '1', valueClass: 'text-cyan-300' })
          ])
        ])
      ])
    ]);

  ReactDOM.createRoot(document.getElementById('root')).render(e(Dashboard));
</script>
"""

html = html.replace("__MAP_DATA__", map_data_json)

components.html(
    html,
    height=1180,
    scrolling=True,
)
