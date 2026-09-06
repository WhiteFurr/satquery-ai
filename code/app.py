import base64
import html
import os

import streamlit as st

from controller import CentralController


st.set_page_config(
    page_title="SatQuery AI | Satellite Intelligence Platform",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def load_controller():
    return CentralController()


controller = load_controller()
os.makedirs("data/uploads", exist_ok=True)


def save_upload(uploaded_file):
    path = f"data/uploads/{uploaded_file.name}"
    with open(path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    return path


def image_data_uri(path):
    if not os.path.exists(path):
        return ""
    extension = os.path.splitext(path)[1].lower().lstrip(".")
    mime = "jpeg" if extension in {"jpg", "jpeg"} else extension
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("ascii")
    return f"data:image/{mime};base64,{encoded}"


def render_trace(log):
    if not log:
        return
    entry = log[0] if isinstance(log, list) else log
    task = html.escape(str(entry.get("task", "Awaiting task")))
    model = html.escape(str(entry.get("model", "Controller")))
    modalities = html.escape(str(entry.get("modalities", "Multimodal")))
    st.markdown(
        f"""
        <div class="telemetry">
            <span class="telemetry-label">ROUTE TRACE</span>
            <span><b>TASK</b>{task}</span>
            <span><b>MODEL</b>{model}</span>
            <span><b>MODALITY</b>{modalities}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result(result, label="INTELLIGENCE OUTPUT", accent="cyan"):
    safe_result = html.escape(str(result)).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="result-card result-{accent}">
            <div class="result-kicker"><span class="result-pulse"></span>{label}</div>
            <div class="result-text">{safe_result}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status(text, kind="success"):
    st.markdown(
        f'<div class="status status-{kind}"><span></span>{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


hero_image = image_data_uri("data/demo_images/satellite_1.jpg")
hero_style = f' style="--hero-image: url({hero_image})"' if hero_image else ""

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --ink:#071016; --panel:rgba(15,31,40,.78); --line:rgba(143,214,224,.18); --muted:#8da4aa; --white:#eef8f5; --cyan:#7de4e8; --mint:#a7f3ce; --amber:#f5bd72; --coral:#ff917b; }
    .stApp { background:radial-gradient(circle at 80% 4%,rgba(41,113,123,.2),transparent 28rem),linear-gradient(135deg,#071016 0%,#0a1820 52%,#071016 100%); color:var(--white); }
    .stApp::before { content:"";position:fixed;inset:0;pointer-events:none;opacity:.28;background-image:linear-gradient(rgba(125,228,232,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(125,228,232,.045) 1px,transparent 1px);background-size:48px 48px;mask-image:linear-gradient(to bottom,black,transparent 76%); }
    [data-testid="stAppViewContainer"] > .main { padding-top:1.5rem; }
    [data-testid="stHeader"] { background:transparent; }
    [data-testid="stSidebar"] { background:#09151d;border-right:1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { padding:1.25rem 1rem; }
    p,label,.stMarkdown,.stCaption { font-family:'Manrope',sans-serif; }
    h1,h2,h3,h4 { font-family:'Manrope',sans-serif;letter-spacing:-.04em;color:var(--white); }
    .block-container { max-width:1420px;padding-left:3.5rem;padding-right:3.5rem; }
    [data-testid="stIconMaterial"] { font-family:'Material Symbols Outlined' !important; }
    .brand { display:flex;align-items:center;gap:.7rem;margin-bottom:2.2rem; }
    .brand-mark { width:38px;height:38px;display:grid;place-items:center;color:var(--ink);background:var(--cyan);font-size:1.45rem;font-weight:800;transform:rotate(45deg); }
    .brand-mark span { transform:rotate(-45deg); }
    .brand-name { font-size:1.05rem;letter-spacing:.1em;font-weight:800;color:var(--white); }
    .brand-name small { display:block;color:var(--muted);font:.58rem 'DM Mono',monospace;letter-spacing:.16em;margin-top:.18rem; }
    .side-label { color:var(--cyan);font:.64rem 'DM Mono',monospace;letter-spacing:.14em;margin:1.35rem 0 .7rem; }
    .side-copy { color:var(--muted);font-size:.78rem;line-height:1.7; }
    .registry { border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:.45rem 0; }
    .registry-row { display:flex;justify-content:space-between;padding:.56rem 0;color:var(--muted);font:.68rem 'DM Mono',monospace; }
    .registry-row b { color:var(--white);font-weight:500; }
    .registry-row em { color:var(--mint);font-style:normal; }
    .github-link { display:block;color:var(--cyan) !important;font:.72rem 'DM Mono',monospace;text-decoration:none;margin-top:1rem; }
    .hero { min-height:440px;position:relative;overflow:hidden;display:flex;align-items:flex-end;padding:3rem;margin-bottom:1.25rem;border:1px solid rgba(125,228,232,.25);background:linear-gradient(90deg,rgba(5,16,22,.97) 0%,rgba(5,16,22,.76) 42%,rgba(5,16,22,.28) 100%),var(--hero-image) center/cover; }
    .hero::after { content:"";position:absolute;inset:0;background:linear-gradient(0deg,rgba(4,14,19,.8),transparent 58%);pointer-events:none; }
    .hero-content { position:relative;z-index:1;max-width:730px; }
    .eyebrow { color:var(--cyan);font:.68rem 'DM Mono',monospace;letter-spacing:.18em;text-transform:uppercase; }
    .hero h1 { font-size:clamp(3.2rem,7vw,6.8rem);line-height:.9;margin:.7rem 0 .9rem;font-weight:800; }
    .hero-title { color:var(--mint);font-size:1.1rem;font-weight:600;letter-spacing:.04em; }
    .hero-copy { max-width:650px;color:#c1d2d2;font-size:1rem;line-height:1.7;margin:.9rem 0 1.6rem; }
    .hero-meta { display:flex;flex-wrap:wrap;gap:.65rem;color:var(--muted);font:.64rem 'DM Mono',monospace; }
    .hero-meta span { border:1px solid var(--line);padding:.45rem .65rem;background:rgba(7,16,22,.45); }
    .hero-meta i { color:var(--mint);font-style:normal; }
    .live-line { position:absolute;z-index:2;top:1.2rem;right:1.3rem;color:var(--mint);font:.62rem 'DM Mono',monospace;letter-spacing:.12em; }
    .live-line::before { content:"";display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--mint);box-shadow:0 0 14px var(--mint);margin-right:.45rem;animation:blink 1.8s infinite; }
    @keyframes blink { 50% { opacity:.28; } }
    .section-kicker { color:var(--cyan);font:.68rem 'DM Mono',monospace;letter-spacing:.15em;margin:2.8rem 0 .5rem; }
    .section-title { font-size:2rem;margin:0 0 .45rem; }
    .section-copy { color:var(--muted);font-size:.9rem;margin:0 0 1.4rem; }
    .cap-card { min-height:154px;padding:1.15rem;border:1px solid var(--line);background:linear-gradient(145deg,rgba(22,48,58,.78),rgba(10,24,31,.82));transition:transform .2s ease,border-color .2s ease; }
    .cap-card:hover { transform:translateY(-4px);border-color:var(--cyan); }
    .cap-icon { color:var(--cyan);font:1.35rem 'DM Mono',monospace; }
    .cap-card h3 { font-size:1rem;margin:.85rem 0 .35rem;letter-spacing:-.02em; }
    .cap-card p { color:var(--muted);font-size:.76rem;line-height:1.55;margin:0; }
    .workspace-nav { display:flex;flex-wrap:wrap;gap:.55rem;margin:1rem 0 3rem; }
    .workspace-nav a { color:var(--white);border:1px solid var(--line);background:rgba(17,37,47,.64);padding:.65rem .9rem;font:.68rem 'DM Mono',monospace;text-decoration:none; }
    .workspace-nav a:hover { color:var(--cyan);border-color:var(--cyan); }
    .workspace { scroll-margin-top:2rem;border-top:1px solid var(--line);padding:2.4rem 0 3rem; }
    .workspace-head { display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;margin-bottom:1.3rem; }
    .workspace-index { color:var(--amber);font:.72rem 'DM Mono',monospace;letter-spacing:.1em;padding-top:.45rem; }
    .workspace h2 { font-size:2rem;margin:0; }
    .workspace-intro { color:var(--muted);max-width:620px;font-size:.88rem;line-height:1.65;margin:.5rem 0 0; }
    .glass { border:1px solid var(--line);background:var(--panel);padding:1.35rem; }
    .glass-dark { background:rgba(5,16,22,.56); }
    .upload-heading { display:flex;gap:.7rem;align-items:center;margin-bottom:.75rem; }
    .upload-number { display:grid;place-items:center;width:28px;height:28px;color:var(--ink);background:var(--cyan);font:.7rem 'DM Mono',monospace; }
    .upload-heading strong { display:block;font-size:.82rem;color:var(--white); }
    .upload-heading small { display:block;color:var(--muted);font-size:.68rem;margin-top:.15rem; }
    [data-testid="stFileUploaderDropzone"] { min-height:126px;border:1px dashed rgba(125,228,232,.38) !important;background:rgba(9,24,31,.72) !important;border-radius:0 !important; }
    [data-testid="stFileUploaderDropzone"] small,[data-testid="stFileUploaderDropzone"] span { color:var(--muted) !important; }
    [data-testid="stFileUploaderDropzone"] button { color:var(--ink) !important;background:var(--cyan) !important;border:0 !important;border-radius:0 !important; }
    .stTextInput input,.stTextArea textarea { color:var(--white) !important;background:rgba(5,16,22,.72) !important;border:1px solid var(--line) !important;border-radius:0 !important;font-family:'DM Mono',monospace !important; }
    .stTextInput label,.stTextArea label { color:var(--muted) !important;font-size:.72rem !important; }
    .stButton > button { width:100%;color:var(--ink);background:var(--cyan);border:0;border-radius:0;font:700 .7rem 'DM Mono',monospace;letter-spacing:.1em;padding:.78rem 1rem; }
    .stButton > button:hover { color:var(--ink);background:var(--mint);border:0; }
    .result-card { margin-top:1rem;padding:1.4rem;border:1px solid rgba(125,228,232,.35);background:linear-gradient(135deg,rgba(23,58,67,.9),rgba(10,27,35,.95)); }
    .result-amber { border-color:rgba(245,189,114,.45);background:linear-gradient(135deg,rgba(64,48,30,.72),rgba(19,29,32,.95)); }
    .result-mint { border-color:rgba(167,243,206,.4);background:linear-gradient(135deg,rgba(27,61,55,.72),rgba(10,28,31,.95)); }
    .result-kicker { color:var(--cyan);font:.64rem 'DM Mono',monospace;letter-spacing:.13em;margin-bottom:.8rem; }
    .result-amber .result-kicker { color:var(--amber); }
    .result-mint .result-kicker { color:var(--mint); }
    .result-pulse { display:inline-block;width:6px;height:6px;margin-right:.45rem;background:currentColor;box-shadow:0 0 10px currentColor; }
    .result-text { color:var(--white);font-size:1.04rem;line-height:1.75; }
    .telemetry { display:flex;flex-wrap:wrap;gap:.9rem;color:var(--muted);font:.62rem 'DM Mono',monospace;border:1px solid var(--line);border-top:0;padding:.72rem 1rem; }
    .telemetry-label { color:var(--mint); }
    .telemetry b { color:var(--cyan);font-weight:400;margin-right:.35rem; }
    .status { margin-top:.85rem;color:var(--mint);font:.66rem 'DM Mono',monospace;letter-spacing:.07em; }
    .status span { display:inline-block;width:6px;height:6px;margin-right:.45rem;background:currentColor;border-radius:50%;box-shadow:0 0 8px currentColor; }
    .status-error { color:var(--coral); }
    .prompt-label { color:var(--muted);font:.65rem 'DM Mono',monospace;letter-spacing:.1em;margin:1.2rem 0 .5rem; }
    .prompt { display:inline-block;color:var(--cyan);border:1px solid var(--line);padding:.42rem .6rem;margin:0 .35rem .35rem 0;font:.66rem 'DM Mono',monospace; }
    .preview-label { color:var(--muted);font:.62rem 'DM Mono',monospace;letter-spacing:.12em;margin:.95rem 0 .5rem; }
    .fusion-flow { display:flex;align-items:center;justify-content:center;gap:.7rem;color:var(--cyan);font:1.3rem 'DM Mono',monospace;margin:.4rem 0; }
    .fusion-flow span { color:var(--muted);font-size:.62rem;letter-spacing:.08em; }
    .fusion-callout { padding:1.25rem;border:1px solid rgba(245,189,114,.55);background:radial-gradient(circle at 92% 0%,rgba(245,189,114,.16),transparent 18rem),rgba(43,34,25,.65); }
    .fusion-callout .eyebrow { color:var(--amber); }
    .fusion-callout h3 { font-size:1.3rem;margin:.5rem 0; }
    .fusion-callout p { color:var(--muted);font-size:.78rem;line-height:1.6; }
    .stAlert { border-radius:0 !important; }
    @media (max-width:800px) { .block-container { padding-left:1rem;padding-right:1rem; } .hero { min-height:500px;padding:1.5rem; } .hero h1 { font-size:3.3rem; } .workspace-head { display:block; } .workspace-index { margin-bottom:.8rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark"><span>◈</span></div><div class="brand-name">SATQUERY AI<small>ORBITAL INTELLIGENCE</small></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-label">MODEL REGISTRY / ONLINE</div>', unsafe_allow_html=True)
    st.markdown('<div class="registry"><div class="registry-row"><b>VISION QA</b><em>BLIP + LoRA</em></div><div class="registry-row"><b>CAPTION ENGINE</b><em>BLIP + LoRA</em></div><div class="registry-row"><b>CHANGE ANALYSIS</b><em>DIFF / VQA</em></div><div class="registry-row"><b>FUSION CORE</b><em>RESNET-18</em></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-label">PROJECT BRIEF</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-copy">A domain-adapted intelligence layer for Earth observation imagery. Query optical and SAR scenes through a single mission control surface.</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-label">SYSTEM</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-copy">Mission state: <span style="color:#a7f3ce">READY</span><br>Input channel: IMAGE / RASTER<br>Output mode: GROUNDED TEXT</div>', unsafe_allow_html=True)
    st.markdown('<a class="github-link" href="#">↗ VIEW PROJECT REPOSITORY</a>', unsafe_allow_html=True)


st.markdown(f'<section class="hero"{hero_style}><div class="live-line">● SYSTEM NOMINAL / ORBITAL FEED</div><div class="hero-content"><div class="eyebrow">EARTH OBSERVATION / INTELLIGENCE OPERATIONS</div><h1>SATQUERY<br>AI</h1><div class="hero-title">Satellite Intelligence Platform</div><p class="hero-copy">Understand, analyze and query Earth Observation imagery using Vision-Language Models, Change Detection and Optical-SAR Fusion.</p><div class="hero-meta"><span><i>01</i> QUERY SCENE</span><span><i>02</i> COMPARE CHANGE</span><span><i>03</i> FUSE SIGNALS</span></div></div></section>', unsafe_allow_html=True)
st.markdown('<div class="section-kicker">CAPABILITY MATRIX / 04 MODULES</div><h2 class="section-title">One platform. Every observation.</h2><p class="section-copy">Select an intelligence workspace below to begin a new analysis pass.</p>', unsafe_allow_html=True)

capabilities = [("01", "◌", "Visual Question Answering", "Ask direct questions about land cover, structures, water, roads and more."), ("02", "≋", "Image Captioning", "Turn a satellite scene into a detailed, readable intelligence report."), ("03", "◐", "Change Detection", "Compare two acquisitions and surface meaningful visual change."), ("04", "⊕", "Optical-SAR Fusion", "Combine complementary signals for richer land-cover classification.")]
cap_columns = st.columns(4)
for column, (number, icon, title, description) in zip(cap_columns, capabilities):
    with column:
        st.markdown(f'<div class="cap-card"><div class="cap-icon">{icon} <small>{number}</small></div><h3>{title}</h3><p>{description}</p></div>', unsafe_allow_html=True)
st.markdown('<nav class="workspace-nav"><a href="#visual-qa">01 / VISUAL QA</a><a href="#captioning">02 / CAPTIONING</a><a href="#change-detection">03 / CHANGE DETECTION</a><a href="#optical-sar-fusion">04 / OPTICAL-SAR FUSION</a></nav>', unsafe_allow_html=True)


st.markdown('<section id="visual-qa" class="workspace"><div class="workspace-head"><div><div class="workspace-index">WORKSPACE 01 / SINGLE-SCENE INQUIRY</div><h2>Visual Question Answering</h2><p class="workspace-intro">Point the platform at one image and ask a precise question. The routed vision model returns a grounded answer for the scene in view.</p></div></div></section>', unsafe_allow_html=True)
vqa_input, vqa_output = st.columns([1.05, .95], gap="large")
with vqa_input:
    st.markdown('<div class="glass"><div class="upload-heading"><div class="upload-number">01</div><div><strong>SCENE INPUT</strong><small>OPTICAL OR SAR / TIF, TIFF, JPG, PNG</small></div></div>', unsafe_allow_html=True)
    vqa_image = st.file_uploader("Upload scene image", type=["tif", "tiff", "jpg", "png"], key="vqa_img", label_visibility="collapsed")
    st.markdown('<div class="prompt-label">SUGGESTED QUERIES</div><span class="prompt">Is there a river visible?</span><span class="prompt">Is this urban or rural?</span><span class="prompt">What land cover dominates this image?</span><span class="prompt">Are roads present?</span>', unsafe_allow_html=True)
    vqa_question = st.text_input("Question", placeholder="Ask the scene anything...", key="vqa_q")
    if vqa_image:
        st.markdown('<div class="preview-label">LIVE PREVIEW</div>', unsafe_allow_html=True)
        st.image(vqa_image, use_container_width=True)
    vqa_execute = st.button("RUN VISUAL QUERY  →", key="vqa_btn")
    st.markdown('</div>', unsafe_allow_html=True)
with vqa_output:
    st.markdown('<div class="glass glass-dark"><div class="eyebrow">ANSWER CHANNEL / VQA</div><p class="section-copy">The resolved answer will appear here with its model route and modality trace.</p>', unsafe_allow_html=True)
    if vqa_execute:
        if not vqa_image or not vqa_question:
            render_status("UPLOAD AN IMAGE AND ENTER A QUESTION", "error")
        else:
            with st.spinner("Routing visual query..."):
                try:
                    vqa_path = save_upload(vqa_image)
                    result, log = controller.route(vqa_question, [vqa_path])
                    render_result(result)
                    render_trace(log)
                    render_status("QUERY RESOLVED")
                except Exception as error:
                    render_status(f"EXECUTION FAILED: {error}", "error")
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<section id="captioning" class="workspace"><div class="workspace-head"><div><div class="workspace-index">WORKSPACE 02 / SCENE REPORT</div><h2>Image Captioning</h2><p class="workspace-intro">Generate a clear scene description that translates raw observation imagery into a concise operational readout.</p></div></div></section>', unsafe_allow_html=True)
cap_input, cap_output = st.columns([.9, 1.1], gap="large")
with cap_input:
    st.markdown('<div class="glass"><div class="upload-heading"><div class="upload-number">02</div><div><strong>OBSERVATION INPUT</strong><small>SCENE TO DESCRIBE</small></div></div>', unsafe_allow_html=True)
    caption_image = st.file_uploader("Upload caption image", type=["tif", "tiff", "jpg", "png"], key="cap_img", label_visibility="collapsed")
    if caption_image:
        st.image(caption_image, use_container_width=True)
    caption_execute = st.button("GENERATE SCENE REPORT  →", key="cap_btn")
    st.markdown('</div>', unsafe_allow_html=True)
with cap_output:
    st.markdown('<div class="glass glass-dark"><div class="eyebrow">REPORT CHANNEL / CAPTION ENGINE</div><p class="section-copy">A generated description of the observed scene will be formatted as an intelligence report.</p>', unsafe_allow_html=True)
    if caption_execute:
        if not caption_image:
            render_status("UPLOAD AN IMAGE FIRST", "error")
        else:
            with st.spinner("Generating scene report..."):
                try:
                    caption_path = save_upload(caption_image)
                    result, log = controller.route("Describe this image", [caption_path])
                    render_result(result, "AI-GENERATED SCENE REPORT", "mint")
                    render_trace(log)
                    render_status("CAPTION GENERATED")
                except Exception as error:
                    render_status(f"EXECUTION FAILED: {error}", "error")
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<section id="change-detection" class="workspace"><div class="workspace-head"><div><div class="workspace-index">WORKSPACE 03 / TEMPORAL COMPARISON</div><h2>Change Detection</h2><p class="workspace-intro">Place two captures of the same location side by side. The comparison engine will describe the change and expose its pixel-level evidence.</p></div></div></section>', unsafe_allow_html=True)
before_col, change_center, after_col = st.columns([1, .12, 1], gap="medium")
with before_col:
    st.markdown('<div class="glass"><div class="upload-heading"><div class="upload-number">A</div><div><strong>BEFORE CAPTURE</strong><small>EARLIER ACQUISITION</small></div></div>', unsafe_allow_html=True)
    before_image = st.file_uploader("Before image", type=["tif", "tiff", "jpg", "png"], key="before_img", label_visibility="collapsed")
    if before_image:
        st.image(before_image, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with change_center:
    st.markdown('<div class="fusion-flow" style="height:100%;">↔<span>DIFF</span></div>', unsafe_allow_html=True)
with after_col:
    st.markdown('<div class="glass"><div class="upload-heading"><div class="upload-number">B</div><div><strong>AFTER CAPTURE</strong><small>LATER ACQUISITION</small></div></div>', unsafe_allow_html=True)
    after_image = st.file_uploader("After image", type=["tif", "tiff", "jpg", "png"], key="after_img", label_visibility="collapsed")
    if after_image:
        st.image(after_image, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
change_question = st.text_input("Comparison query", value="What changed between these images?", key="change_q")
change_execute = st.button("COMPARE ACQUISITIONS  →", key="change_btn")
if change_execute:
    if not before_image or not after_image:
        render_status("UPLOAD BOTH A BEFORE AND AFTER IMAGE", "error")
    else:
        with st.spinner("Comparing acquisitions..."):
            try:
                before_path, after_path = save_upload(before_image), save_upload(after_image)
                result, log = controller.route(change_question, [before_path, after_path])
                render_result(result, "TEMPORAL ANALYSIS", "amber")
                render_trace(log)
                if os.path.exists("outputs/change_mask.png"):
                    st.markdown('<div class="glass" style="margin-top:1rem"><div class="eyebrow">EVIDENCE LAYER / CHANGE MASK</div><p class="section-copy">Highlighted regions indicate detected pixel-level change.</p>', unsafe_allow_html=True)
                    st.image("outputs/change_mask.png", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                render_status("COMPARISON COMPLETE")
            except Exception as error:
                render_status(f"EXECUTION FAILED: {error}", "error")


st.markdown('<section id="optical-sar-fusion" class="workspace"><div class="workspace-head"><div><div class="workspace-index">WORKSPACE 04 / MULTI-SENSOR INTELLIGENCE</div><h2>Optical-SAR Fusion</h2><p class="workspace-intro">Bring together optical texture and radar structure for a richer view of the terrain. This is the platform’s multi-sensor classification channel.</p></div></div></section>', unsafe_allow_html=True)
sar_col, plus_col, optical_col = st.columns([1, .13, 1], gap="medium")
with sar_col:
    st.markdown('<div class="glass"><div class="upload-heading"><div class="upload-number">S1</div><div><strong>SENTINEL-1 / SAR</strong><small>RADAR SIGNAL / TIF, TIFF</small></div></div>', unsafe_allow_html=True)
    sar_image = st.file_uploader("SAR image", type=["tif", "tiff"], key="sar_img", label_visibility="collapsed")
    if sar_image:
        st.image(sar_image, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with plus_col:
    st.markdown('<div class="fusion-flow" style="height:100%;">+<span>FUSE</span></div>', unsafe_allow_html=True)
with optical_col:
    st.markdown('<div class="glass"><div class="upload-heading"><div class="upload-number">S2</div><div><strong>SENTINEL-2 / OPTICAL</strong><small>VISIBLE SPECTRUM / TIF, TIFF, JPG, PNG</small></div></div>', unsafe_allow_html=True)
    optical_image = st.file_uploader("Optical image", type=["tif", "tiff", "jpg", "png"], key="opt_img", label_visibility="collapsed")
    if optical_image:
        st.image(optical_image, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
fusion_query = st.text_input("Fusion query", value="Classify this location", key="fusion_q")
fusion_execute = st.button("RUN FUSION ANALYSIS  →", key="fusion_btn")
st.markdown('<div class="fusion-callout"><div class="eyebrow">SENTINEL FUSION CORE</div><h3>Two signals. One intelligence layer.</h3><p>Optical context and SAR response are routed together for land-cover classification. Upload a matched pair to activate the analysis channel.</p></div>', unsafe_allow_html=True)
if fusion_execute:
    if not optical_image or not sar_image:
        render_status("UPLOAD BOTH SENTINEL-1 SAR AND SENTINEL-2 OPTICAL INPUTS", "error")
    else:
        with st.spinner("Running joint classification..."):
            try:
                optical_path, sar_path = save_upload(optical_image), save_upload(sar_image)
                result, log = controller.route(fusion_query, [optical_path, sar_path])
                render_result(result, "FUSION INTELLIGENCE / CLASSIFICATION", "amber")
                render_trace(log)
                render_status("CLASSIFICATION COMPLETE")
            except Exception as error:
                render_status(f"EXECUTION FAILED: {error}", "error")