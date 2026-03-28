# I Want to Deploy My Project

## The Problem
I've built something and want to deploy it with one command.

## For Web Apps (Vercel)

```bash
# First time setup
oos deploy init vercel

# Deploy
oos deploy vercel

# That's it!
```

## For Backend/Services (OCI VM)

```bash
# First time setup (configure VM connection)
oos deploy init oci

# Deploy
oos deploy oci

# That's it!
```

## What Happens

**Vercel deployment:**
1. Detects project type (Next.js, React, etc.)
2. Builds project
3. Deploys to Vercel
4. Returns deployment URL

**OCI VM deployment:**
1. Builds Docker container (if needed)
2. Transfers to VM via SSH
3. Starts service
4. Returns service URL

## Requirements

**For Vercel:**
- Vercel account (free tier available)
- `vercel` CLI installed (auto-installed by OOS)

**For OCI VM:**
- Oracle Cloud account (free tier available)
- VM running (OOS can provision one)
- SSH access configured

## Troubleshooting

**"Vercel not authenticated"**
```bash
vercel login
```

**"Cannot connect to VM"**
```bash
# Check SSH config
ssh -i ~/.ssh/oci_key user@vm-ip

# Fix permissions
chmod 600 ~/.ssh/oci_key
```

**"Deployment failed"**
```bash
# Check logs
oos deploy logs

# Retry with debug
oos deploy vercel --debug
```
