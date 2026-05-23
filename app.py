import streamlit as st
import plotly.graph_objects as go
import requests, re

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SS Prediction Tool",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 3D animated background + global CSS ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* ── canvas background ── */
#dna-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    z-index: 0;
    pointer-events: none;
}

/* ── push streamlit content above canvas ── */
.stApp { background: transparent !important; }
[data-testid="stAppViewContainer"] { background: transparent !important; }
[data-testid="stHeader"] { background: transparent !important; }
section[data-testid="stSidebar"] {
    background: rgba(10, 22, 40, 0.82) !important;
    backdrop-filter: blur(14px);
    border-right: 1px solid rgba(29,158,117,0.25);
    z-index: 10;
}
.main .block-container {
    background: transparent !important;
    padding-top: 1.5rem;
    z-index: 10;
    position: relative;
}

/* ── cards ── */
.ss-card {
    background: rgba(10, 22, 40, 0.75);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(29,158,117,0.30);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
    color: #e2f0eb;
}
.ss-card h4 {
    font-size: 12px;
    font-weight: 500;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: #5DCAA5;
    margin: 0 0 12px 0;
}

/* ── metric pill ── */
.metric-pill {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    background: rgba(29,158,117,0.12);
    border: 1px solid rgba(29,158,117,0.30);
    border-radius: 10px;
    padding: 10px 18px;
    min-width: 80px;
    margin: 4px;
}
.metric-pill .val { font-size: 22px; font-weight: 600; color: #5DCAA5; }
.metric-pill .lbl { font-size: 11px; color: #8ab8a8; margin-top: 2px; }

/* ── q3 badge ── */
.q3-badge {
    background: linear-gradient(135deg,rgba(29,158,117,0.25),rgba(29,158,117,0.08));
    border: 1px solid rgba(29,158,117,0.5);
    border-radius: 12px;
    padding: 14px 20px;
    text-align: center;
    margin-bottom: 14px;
}
.q3-badge .big { font-size: 40px; font-weight: 700; color: #5DCAA5; line-height: 1; }
.q3-badge .sub { font-size: 12px; color: #8ab8a8; margin-top: 4px; }

/* ── seq box ── */
.seq-box {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.9;
    background: rgba(0,0,0,0.30);
    border-radius: 8px;
    padding: 12px 14px;
    border: 1px solid rgba(255,255,255,0.07);
    overflow-x: auto;
    white-space: pre;
    color: #c8ddd6;
}
.seq-abs  { color: #60a5fa; }
.seq-pred { color: #5DCAA5; }

/* ── nav arrows ── */
.nav-row {
    display: flex; align-items: center;
    justify-content: space-between;
    margin-top: 10px;
    font-size: 12px; color: #8ab8a8;
}

/* ── sidebar labels ── */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p {
    color: #c8ddd6 !important;
    font-size: 13px !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(29,158,117,0.35) !important;
    color: #e2f0eb !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton button {
    background: #1D9E75 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 10px !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #0F6E56 !important;
}

/* title */
.app-title {
    font-size: 22px; font-weight: 700;
    color: #5DCAA5;
    margin-bottom: 2px;
}
.app-sub { font-size: 13px; color: #8ab8a8; margin-bottom: 18px; }

/* run badge */
.run-badge {
    display:inline-block;
    background:rgba(29,158,117,0.18);
    border:1px solid rgba(29,158,117,0.40);
    border-radius:20px;
    padding:3px 12px;
    font-size:11px;
    color:#5DCAA5;
    margin-bottom:10px;
}

/* streamlit general text */
.stMarkdown, .stText, p { color: #c8ddd6 !important; }
h1,h2,h3 { color: #5DCAA5 !important; }
</style>

<!-- 3D DNA / molecule floating particle canvas -->
<canvas id="dna-canvas"></canvas>
<script>
(function(){
const canvas = document.getElementById('dna-canvas');
const ctx    = canvas.getContext('2d');

function resize(){ canvas.width=window.innerWidth; canvas.height=window.innerHeight; }
resize();
window.addEventListener('resize', resize);

/* ── particle config ── */
const N = 90;
const particles = [];
const teal  = 'rgba(29,158,117,';
const blue  = 'rgba(56,138,221,';
const white = 'rgba(200,220,215,';

for(let i=0;i<N;i++){
    particles.push({
        x: Math.random()*2000,
        y: Math.random()*1200,
        z: Math.random()*800+100,
        vx:(Math.random()-.5)*0.4,
        vy:(Math.random()-.5)*0.3,
        vz:(Math.random()-.5)*0.5,
        r: Math.random()*2+1,
        col: [teal,blue,white][Math.floor(Math.random()*3)],
        pulse: Math.random()*Math.PI*2,
        pspeed: Math.random()*0.02+0.01,
    });
}

/* ── DNA helix strands ── */
const helixCount = 3;
const helixPts   = [];
for(let h=0;h<helixCount;h++){
    helixPts.push({
        cx: 180 + h * 350,
        cy: 300 + (h%2)*120,
        phase: h*1.2,
        amp: 55,
        freq: 0.022,
        speed: 0.008 + h*0.003,
        t: 0,
    });
}

let frame = 0;

function project(x, y, z){
    const fov = 500;
    const scale = fov / (fov + z);
    return { sx: x*scale, sy: y*scale, scale };
}

function draw(){
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0,0,W,H);

    /* very subtle dark overlay — let streamlit bg show */
    ctx.fillStyle='rgba(4,14,28,0.55)';
    ctx.fillRect(0,0,W,H);

    /* ── draw connecting lines between nearby particles ── */
    for(let i=0;i<particles.length;i++){
        const a = particles[i];
        const pa = project(a.x, a.y, a.z);
        for(let j=i+1;j<particles.length;j++){
            const b = particles[j];
            const dx=a.x-b.x, dy=a.y-b.y, dz=a.z-b.z;
            const dist=Math.sqrt(dx*dx+dy*dy+dz*dz);
            if(dist<160){
                const pb = project(b.x, b.y, b.z);
                const alpha = (1-dist/160)*0.18;
                ctx.beginPath();
                ctx.moveTo(pa.sx, pa.sy);
                ctx.lineTo(pb.sx, pb.sy);
                ctx.strokeStyle=`rgba(29,158,117,${alpha})`;
                ctx.lineWidth=0.6;
                ctx.stroke();
            }
        }
    }

    /* ── draw particles ── */
    particles.forEach(p=>{
        p.x+=p.vx; p.y+=p.vy; p.z+=p.vz;
        p.pulse+=p.pspeed;
        if(p.x<0||p.x>2000) p.vx*=-1;
        if(p.y<0||p.y>1400) p.vy*=-1;
        if(p.z<100||p.z>900) p.vz*=-1;

        const pr = project(p.x, p.y, p.z);
        const glow = 0.5 + 0.5*Math.sin(p.pulse);
        const r = p.r * pr.scale * 1.8;

        ctx.beginPath();
        ctx.arc(pr.sx, pr.sy, r, 0, Math.PI*2);
        ctx.fillStyle = p.col + (0.5+glow*0.4)+')';
        ctx.fill();

        /* glow ring */
        ctx.beginPath();
        ctx.arc(pr.sx, pr.sy, r*2.5, 0, Math.PI*2);
        ctx.fillStyle = p.col + (0.06*glow)+')';
        ctx.fill();
    });

    /* ── DNA double helix strands ── */
    helixPts.forEach(h=>{
        h.t += h.speed;
        const pts1=[], pts2=[];
        for(let i=0;i<80;i++){
            const angle = i*h.freq*Math.PI*2 + h.t + h.phase;
            const y = (i/80)*H;
            pts1.push({ x: h.cx + Math.cos(angle)*h.amp, y });
            pts2.push({ x: h.cx + Math.cos(angle+Math.PI)*h.amp, y });
        }

        /* strand 1 */
        ctx.beginPath();
        pts1.forEach((p,i)=>{ i===0?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y); });
        ctx.strokeStyle='rgba(29,158,117,0.22)';
        ctx.lineWidth=1.5; ctx.stroke();

        /* strand 2 */
        ctx.beginPath();
        pts2.forEach((p,i)=>{ i===0?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y); });
        ctx.strokeStyle='rgba(56,138,221,0.18)';
        ctx.lineWidth=1.5; ctx.stroke();

        /* rungs */
        for(let i=0;i<80;i+=5){
            ctx.beginPath();
            ctx.moveTo(pts1[i].x, pts1[i].y);
            ctx.lineTo(pts2[i].x, pts2[i].y);
            ctx.strokeStyle='rgba(93,202,165,0.14)';
            ctx.lineWidth=1; ctx.stroke();

            /* node dots */
            [pts1[i], pts2[i]].forEach(p=>{
                ctx.beginPath();
                ctx.arc(p.x, p.y, 2.5, 0, Math.PI*2);
                ctx.fillStyle='rgba(93,202,165,0.55)';
                ctx.fill();
            });
        }
    });

    frame++;
    requestAnimationFrame(draw);
}
draw();
})();
</script>
""", unsafe_allow_html=True)

# ── Local algorithm imports ───────────────────────────────────────────────
from PDB          import fetch_pdb_sequence
from preprocessing import process_dssp_pipeline
from GOR_I        import GOR_I
from GOR_IV       import GOR_IV
from PHD          import PHD

# ── Session state init ────────────────────────────────────────────────────
for key in ["runs", "result_idx", "graph_idx"]:
    if key not in st.session_state:
        st.session_state[key]       = [] if key == "runs" else 0

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧬 SS Predict")
    st.markdown("---")

    pdb_id = st.text_input("PDB ID", placeholder="e.g. 1HB6").strip().upper()
    dssp_input = st.text_area("DSSP / Secondary Structure Input",
                               height=160,
                               placeholder="Paste DSSP data here...")
    method = st.radio("Prediction Method", ["GOR I", "GOR IV", "PHD"])

    run_clicked = st.button("▶  Run Prediction")
    if st.button("🗑  Clear all runs"):
        st.session_state.runs       = []
        st.session_state.result_idx = 0
        st.session_state.graph_idx  = 0
        st.rerun()

# ── Run prediction ────────────────────────────────────────────────────────
if run_clicked:
    if not pdb_id:
        st.sidebar.error("Please enter a PDB ID.")
    elif not dssp_input.strip():
        st.sidebar.error("Please paste DSSP data.")
    else:
        with st.spinner("Running prediction..."):
            fasta_seq      = fetch_pdb_sequence(pdb_id)
            processed_data = process_dssp_pipeline(dssp_input)

            if isinstance(fasta_seq, str) and fasta_seq.startswith("Error"):
                st.sidebar.error(fasta_seq)
            elif processed_data is None:
                st.sidebar.error("Preprocessing failed — check DSSP input format.")
            else:
                fn = {"GOR I": GOR_I, "GOR IV": GOR_IV, "PHD": PHD}[method]
                result = fn(fasta_seq, processed_data)

                if result and isinstance(result, dict):
                    mid_lines  = result["mid_lines"]
                    next_lines = result["next_lines"]
                    sequence   = result["sequence"]
                    aligned    = result["aligned_output"]

                    # Accuracy
                    pred = mid_lines[2] if len(mid_lines) > 2 else ""
                    abso = next_lines[1].lower() if len(next_lines) > 1 else ""
                    mlen = min(len(pred), len(abso))
                    H = sum(1 for i in range(mlen) if pred[i]=='h' and abso[i]=='h')
                    E = sum(1 for i in range(mlen) if pred[i]=='e' and abso[i]=='e')
                    C = sum(1 for i in range(mlen) if pred[i]=='c' and abso[i]=='c')
                    total = len(sequence)
                    q3 = round((H+E+C)/total*100, 2) if total > 0 else 0.0

                    st.session_state.runs.append({
                        "method":   method,
                        "pdb_id":   pdb_id,
                        "aligned":  aligned,
                        "H": H, "E": E, "C": C,
                        "total":    total,
                        "q3":       q3,
                        "sequence": sequence,
                    })
                    st.session_state.result_idx = len(st.session_state.runs) - 1
                    st.session_state.graph_idx  = len(st.session_state.runs) - 1
                    st.rerun()
                else:
                    st.sidebar.error("Prediction returned no result.")

# ── Main content ──────────────────────────────────────────────────────────
st.markdown('<div class="app-title">Secondary Structure Accuracy Prediction</div>', unsafe_allow_html=True)
st.markdown('<div class="app-sub">Local GOR I · GOR IV · PHD — no external servers</div>', unsafe_allow_html=True)

runs = st.session_state.runs

if not runs:
    st.markdown("""
    <div class="ss-card" style="text-align:center;padding:40px">
        <div style="font-size:48px;margin-bottom:12px">🧬</div>
        <div style="font-size:15px;color:#5DCAA5;font-weight:500">Ready to predict</div>
        <div style="font-size:13px;color:#8ab8a8;margin-top:6px">
            Enter a PDB ID, paste DSSP data, choose a method and click Run.
        </div>
    </div>""", unsafe_allow_html=True)
else:
    total_runs = len(runs)

    # ── Layout: left col (sequence + result) | right col (graph + q3) ──
    col_left, col_right = st.columns([1.15, 1])

    # ────────────────────────────────────────────────────
    # LEFT — Sequence alignment
    # ────────────────────────────────────────────────────
    with col_left:
        ri = st.session_state.result_idx
        run = runs[ri]

        st.markdown(f'<div class="run-badge">Run {ri+1} of {total_runs} — {run["method"]} — {run["pdb_id"]}</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="ss-card">
            <h4>📄 Sequence alignment</h4>
            <div class="seq-box">{run["aligned"]}</div>
        </div>""", unsafe_allow_html=True)

        # Nav arrows
        nav_c1, nav_c2, nav_c3 = st.columns([1,2,1])
        with nav_c1:
            if st.button("◀ Prev", key="res_prev", disabled=(ri==0)):
                st.session_state.result_idx -= 1
                st.rerun()
        with nav_c2:
            st.markdown(f"<div style='text-align:center;font-size:12px;color:#8ab8a8;padding-top:8px'>Result {ri+1} of {total_runs}</div>", unsafe_allow_html=True)
        with nav_c3:
            if st.button("Next ▶", key="res_next", disabled=(ri==total_runs-1)):
                st.session_state.result_idx += 1
                st.rerun()

        # Result summary card
        st.markdown(f"""
        <div class="ss-card" style="margin-top:4px">
            <h4>📊 Accuracy breakdown</h4>
            <div style="display:flex;gap:8px;flex-wrap:wrap">
                <div class="metric-pill"><span class="val" style="color:#60a5fa">{run["H"]}</span><span class="lbl">Helix (H)</span></div>
                <div class="metric-pill"><span class="val" style="color:#f97316">{run["E"]}</span><span class="lbl">Strand (E)</span></div>
                <div class="metric-pill"><span class="val" style="color:#5DCAA5">{run["C"]}</span><span class="lbl">Coil (C)</span></div>
                <div class="metric-pill"><span class="val">{run["total"]}</span><span class="lbl">Total AA</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ────────────────────────────────────────────────────
    # RIGHT — Graph + Q3
    # ────────────────────────────────────────────────────
    with col_right:
        gi = st.session_state.graph_idx
        grun = runs[gi]

        st.markdown(f'<div class="run-badge">Run {gi+1} of {total_runs} — {grun["method"]} — {grun["pdb_id"]}</div>', unsafe_allow_html=True)

        # Q3 badge
        st.markdown(f"""
        <div class="q3-badge">
            <div class="big">{grun["q3"]}%</div>
            <div class="sub">Q3 Accuracy — {grun["method"]}</div>
        </div>""", unsafe_allow_html=True)

        # Plotly bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Helix (H)", "Strand (E)", "Coil (C)"],
            y=[grun["H"], grun["E"], grun["C"]],
            marker_color=["#378ADD","#f97316","#1D9E75"],
            marker_line_width=0,
            text=[grun["H"], grun["E"], grun["C"]],
            textposition="outside",
            textfont=dict(color="#c8ddd6", size=12),
        ))
        fig.add_hline(
            y=grun["q3"], line_dash="dash",
            line_color="#5DCAA5", line_width=1.5,
            annotation_text=f"Q3: {grun['q3']}%",
            annotation_font_color="#5DCAA5",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor ="rgba(0,0,0,0)",
            font=dict(color="#c8ddd6", size=12),
            margin=dict(l=10,r=10,t=10,b=10),
            height=240,
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zeroline=False),
            xaxis=dict(showgrid=False),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Graph nav
        gn1, gn2, gn3 = st.columns([1,2,1])
        with gn1:
            if st.button("◀ Prev", key="g_prev", disabled=(gi==0)):
                st.session_state.graph_idx -= 1
                st.rerun()
        with gn2:
            st.markdown(f"<div style='text-align:center;font-size:12px;color:#8ab8a8;padding-top:8px'>Graph {gi+1} of {total_runs}</div>", unsafe_allow_html=True)
        with gn3:
            if st.button("Next ▶", key="g_next", disabled=(gi==total_runs-1)):
                st.session_state.graph_idx += 1
                st.rerun()

        # All runs summary table
        if total_runs > 1:
            st.markdown("""<div class="ss-card" style="margin-top:8px">
                <h4>📋 All runs comparison</h4>""", unsafe_allow_html=True)
            rows = ""
            for i, r in enumerate(runs):
                active = "color:#5DCAA5;font-weight:500" if i==gi else "color:#8ab8a8"
                rows += f"<tr style='{active}'><td style='padding:4px 8px'>{i+1}</td><td style='padding:4px 8px'>{r['pdb_id']}</td><td style='padding:4px 8px'>{r['method']}</td><td style='padding:4px 8px;color:#5DCAA5'>{r['q3']}%</td></tr>"
            st.markdown(f"""
                <table style='width:100%;font-size:12px;border-collapse:collapse'>
                    <thead><tr style='color:#5DCAA5;font-size:11px'>
                        <th style='text-align:left;padding:4px 8px'>#</th>
                        <th style='text-align:left;padding:4px 8px'>PDB</th>
                        <th style='text-align:left;padding:4px 8px'>Method</th>
                        <th style='text-align:left;padding:4px 8px'>Q3</th>
                    </tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>""", unsafe_allow_html=True)
