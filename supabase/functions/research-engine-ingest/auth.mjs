// Authenticate service callers without logging or embedding credentials.
export async function authenticate(req, env, cryptoImpl = crypto) {
  const legacy = env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
  let named = {};
  try { named = JSON.parse(env.get("SUPABASE_SECRET_KEYS") || "{}"); }
  catch { named = {}; }
  const keys = [
    ...Object.values(named && typeof named === "object" ? named : {}),
    env.get("SUPABASE_SECRET_KEY")
  ].filter(k => typeof k === "string" && k.startsWith("sb_secret_"));
  const supplied = req.headers.get("apikey") || "";
  const bearer = req.headers.get("authorization") || "";
  async function equal(a, b) {
    if (!a || !b) return false;
    const encode = new TextEncoder();
    const [x, y] = await Promise.all([a, b].map(v =>
      cryptoImpl.subtle.digest("SHA-256", encode.encode(v)).then(v => new Uint8Array(v))));
    let diff = 0;
    for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
    return diff === 0;
  }
  if (supplied.startsWith("sb_secret_")) {
    for (const key of keys) {
      if (await equal(supplied, key)) return true;
    }
  }
  return !!legacy && await equal(bearer, "Bearer " + legacy);
}
