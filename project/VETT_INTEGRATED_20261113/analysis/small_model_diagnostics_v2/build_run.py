import sys,json,re,time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"small_model_diagnostics_v2"; O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
SEL=[("match_0031","inn1","Connor Shaw","Evan Vale",4,19,"Leo Shaw",1,26,8),
     ("match_0019","inn2","Ethan Ward","Evan Turner",5,13,"Liam Foster",1,15,6)]
S=[]
for m,inn,bat,A,Aw,Ar,B,Bw,Br,total in SEL:
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); ctrl=L.render(md,0); ss=L.sentences(ctrl)
    def one(c): return next((x for x in ss if c(x)),"")
    dis=one(lambda x:bat+" fell to "+A in x); sumA=one(lambda x:f"{A}, whose {Aw} for {Ar}" in x); sumB=one(lambda x:f"{B} kept the pressure on with {Bw} for {Br}" in x)
    tot=one(lambda x:"closed on" in x and f"for {total}" in x)
    note="Note: the bowling figures above are the pre-revision record."
    innlab="first innings" if inn=="inn1" else "second innings"
    re_n=f"Match review: the dismissal of {bat} in the {innlab} was reassigned from {A} to {B}."
    ret_n=f"Match review: the dismissal of {bat} in the {innlab} was reviewed and the original attribution to {A} was upheld; the wicket remains credited to {A}."
    base=" ".join([dis,sumA,sumB,tot,note])
    S.append({"match":m,"innings":inn,"batter":bat,"A":A,"B":B,"old":{"Aw":Aw,"Bw":Bw,"Ar":Ar,"Br":Br,"total":total},
              "reassign_text":base+" "+re_n,"retain_text":base+" "+ret_n,"reassign_gold":{f"{A}_wickets":Aw-1,f"{B}_wickets":Bw+1},"retain_gold":{f"{A}_wickets":Aw,f"{B}_wickets":Bw},
              "checks":{"distinct":len({(Aw-1,Bw+1),(Aw,Bw),(Bw,Aw),(Aw+1,Bw-1)})==4,"all":all([dis,sumA,sumB,tot])}})
(O/"SAMPLE_MANIFEST.json").write_text(json.dumps(S,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
def direct_prompt(t,s):
    keys=[f"{s['A']}_wickets",f"{s['B']}_wickets"]
    return ("You are a cricket scorer. Read the text and return the two final wicket counts after the review. Return ONLY JSON with keys "+", ".join(keys)+". Integers, no prose.\n\nText:\n"+t+"\n\nJSON:")
def extract_prompt(t,s):
    return ("You are a cricket scorer. Extract the review decision and pre-review facts. Return ONLY JSON with keys decision (reassign|retain|UNKNOWN), dismissed_batter, original_bowler, final_bowler, original_bowler_wickets_before, other_bowler_wickets_before. Strings for names, integers for wickets, UNKNOWN if insufficient. final_bowler may equal original_bowler. No prose.\n\nText:\n"+t+"\n\nJSON:")
def ex(raw):
    if not raw: return None
    s=raw.strip(); i=s.find("{")
    if i<0: return None
    d=0
    for j in range(i,len(s)):
        if s[j]=="{": d+=1
        elif s[j]=="}":
            d-=1
            if d==0:
                try: return json.loads(s[i:j+1])
                except Exception: return None
    return None
out=O/"runs"/"paired.jsonl"; out.parent.mkdir(exist_ok=True)
for s in S:
    for kind in ["direct_reassign","extract_reassign","extract_retain"]:
        text=s["reassign_text"] if "reassign" in kind else s["retain_text"]
        for model in MODELS:
            pr=direct_prompt(text,s) if kind=="direct_reassign" else extract_prompt(text,s)
            service.config.MODEL_TAG=model; info=service.model_info(model) or {}
            try: gen=service.generate(pr,num_ctx=8192,num_predict=400); raw=gen["raw_output"]
            except Exception as e: raw=""; gen={}
            doc=ex(raw) if raw else None
            row={"match":s["match"],"kind":kind,"model":model,"digest":info.get("digest"),"quant":info.get("quantization_level"),
                 "text_chars":len(text),"text_sha256":__import__("hashlib").sha256(text.encode()).hexdigest(),"prompt_sha256":__import__("hashlib").sha256(pr.encode()).hexdigest(),
                 "raw_output":raw,"parsed":doc,"parse_ok":isinstance(doc,dict),"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
            open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n")
            print(s["match"],kind,model.split(":")[0],"parse",row["parse_ok"],flush=True)
print("used 18")
