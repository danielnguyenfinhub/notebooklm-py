Review the implementation against the spec with a security-first lens.

Look for:
1. Any remaining path where a raw `Cookie` header is sent to a dynamic host
2. Any dynamic upload/download URL path that skips validation
3. Any test still normalizing `example.com` as a trusted success path
4. Any documentation drift between README / SECURITY / configuration docs
5. Any unnecessary UX friction beyond the env-var override

Reject the change if:
- validation can be bypassed by userinfo, ports, or IP literals
- tests do not prove the new trust boundary
- docs omit the override path
