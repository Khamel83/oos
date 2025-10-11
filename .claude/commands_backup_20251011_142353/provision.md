---
description: "AI-powered infrastructure provisioning"
tools: ["Bash"]
---

AI-powered infrastructure provisioning

```bash
./bin/provision-infrastructure.sh "$ARGUMENTS"
```

Automatically generates production-ready infrastructure configurations:
- Docker Compose setup with Traefik reverse proxy
- SSL certificate automation with Let's Encrypt
- Production environment variables
- Monitoring and logging setup
- Security hardening recommendations

Supports multiple deployment targets and handles complex networking configurations automatically.

Usage examples:
- `./bin/provision-infrastructure.sh` - Interactive provisioning
- `./bin/provision-infrastructure.sh --preview` - Preview without deploying
- `./bin/provision-infrastructure.sh --deploy` - Deploy directly