import { authenticate } from "./auth.mjs";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
const enc = new TextEncoder();
const hex = (a: ArrayBuffer) => Array.from(new Uint8Array(a)).map(x => x.toString(16).padStart(2,"0")).join("");
const reply = (body: unknown, status=200) => new Response(JSON.stringify(body),{status,headers:{"content-type":"application/json","cache-control":"no-store"}});
Deno.serve(async (req: Request) => {
  if(req.method !== "POST") return reply({error:"method_not_allowed"},405);
  const secret=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!await authenticate(req, Deno.env)) return reply({error:"forbidden"},403);
  if(!secret) return reply({error:"server_configuration"},503);
  const length=Number(req.headers.get("content-length")||0);
  if(length>1500000) return reply({error:"too_large"},413);
  try {
    const b=await req.json();
    const allowed=["candidate","metadata_only","real_iq_descriptive","labeled_measured","verified_benchmark"];
    if(typeof b.run_id!=="string" || !/^[a-zA-Z0-9_-]{3,96}$/.test(b.run_id) ||
       typeof b.dataset_id!=="string" || !/^[a-zA-Z0-9_-]{3,96}$/.test(b.dataset_id) ||
       !allowed.includes(b.evidence_level) || !b.algorithm_version || !b.producer || !b.algorithm ||
       typeof b.artifact_base64!=="string" || b.artifact_base64.length>1400000) return reply({error:"invalid_schema"},400);
    if(b.result?.measured_auc != null && (!b.labels_verified || !b.phase_preserved || !["labeled_measured","verified_benchmark"].includes(b.evidence_level))) return reply({error:"unverified_measured_claim"},400);
    const bytes=Uint8Array.from(atob(b.artifact_base64),c=>c.charCodeAt(0));
    if(bytes.length>1000000) return reply({error:"artifact_too_large"},413);
    const sha=hex(await crypto.subtle.digest("SHA-256",bytes));
    if(sha!==b.artifact_sha256) return reply({error:"checksum_mismatch"},400);
    const client=createClient(Deno.env.get("SUPABASE_URL")!,secret);
    const {data:ds,error:de}=await client.from("research_engine_datasets").select("dataset_id,labels_verified,phase_preserved").eq("dataset_id",b.dataset_id).single();
    if(de || !ds) return reply({error:"unknown_dataset"},400);
    if(b.result?.measured_auc != null && (!ds.labels_verified || !ds.phase_preserved)) return reply({error:"dataset_not_verified"},400);
    const path=b.dataset_id+"/"+b.run_id+"/"+sha+".json";
    const upload=await client.storage.from("research-engine-artifacts").upload(path,bytes,{contentType:"application/json",upsert:false});
    if(upload.error && !/already exists|duplicate/i.test(upload.error.message)) return reply({error:"artifact_storage_failed"},502);
    const insert=await client.from("research_engine_runs").upsert({
      run_id:b.run_id,dataset_id:b.dataset_id,producer:b.producer,algorithm:b.algorithm,
      algorithm_version:b.algorithm_version,evidence_level:b.evidence_level,result:b.result||{},
      artifact_url:"storage://research-engine-artifacts/"+path
    },{onConflict:"run_id",ignoreDuplicates:true});
    if(insert.error) return reply({error:"run_write_failed"},500);
    const receipt=await client.from("research_engine_ingest_receipts").upsert({
      receipt_id:b.run_id+"-"+sha.slice(0,16),run_id:b.run_id,artifact_path:path,artifact_sha256:sha
    },{onConflict:"receipt_id",ignoreDuplicates:true});
    if(receipt.error) return reply({error:"receipt_write_failed"},500);
    return reply({ok:true,run_id:b.run_id,artifact_sha256:sha});
  } catch(_e){return reply({error:"invalid_request"},400);}
});
