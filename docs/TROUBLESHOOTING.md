# Troubleshooting

## 1) GitHub push blocked: secrets detected
**Symptom:**
```
GH013: Push cannot contain secrets … path: .env:XX
```

**Fix:**
```bash
sudo apt install -y git-filter-repo || python3 -m pip install --user git-filter-repo
git filter-repo --force --path .env --path .env.active --path .env.export --invert-paths
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin --force HEAD:master
```

Rotate any exposed tokens in providers. Keep `.env*` out of git (see `.gitignore`).

## 2) 1Password: "not signed in" or session lost
```bash
eval "$(op signin)" && op whoami
```

## 3) Bad env value (common)
- `GITHUB_PAT=...: No such file or directory` inside your 1Password env field.
- Remove trailing error text; keep a single line: `GITHUB_PAT=ghp_xxx` or leave empty.

## 4) CRLF/BOM issues
**Symptom:**
```
.env: line N: $'\r': command not found
```

**Fix:**
```bash
sed -i 's/\r$//' .env
perl -i -pe 's/^\xEF\xBB\xBF//' .env
```

## 5) Archon unreachable
- **Local:**
  ```bash
  curl -4 -I http://localhost:8051/mcp
  ```

- **Remote:**
  ```bash
  curl -4 -I https://archon.yourhost:8051/mcp
  ```

Check firewall, TLS, and that Uvicorn is running on 8051.

## 6) MCPs missing in Claude
At project root:
```bash
claude mcp remove archon || true
claude mcp add --transport http archon $(grep '^ARCHON_URL=' .env.export | cut -d= -f2)
claude mcp list
```

## 7) OpenRouter 401/429
- Use rotation: `OPENROUTER_KEYS=sk1,sk2,sk3`
- Rerun: `.agents/runners/run_claude.sh` (selector picks first working key).