# Auto-Efficiency Constraint

## Automatic Pattern Recognition

When user mentions updating OOS or repository syncing, **immediately** apply learned efficiency patterns without discovery:

### For "update oos" requests:
```bash
# Don't do discovery - just execute:
if [ -d "oos" ]; then
  cd oos && git pull origin master && ./bin/integrate_to_parent.sh
else
  git clone https://github.com/Khamel83/oos.git && cd oos && ./bin/integrate_to_parent.sh
fi
```

### Never Do Manual Discovery:
- ❌ Multiple `git remote -v` checks
- ❌ `ls -la | grep oos` exploration
- ❌ Ask user to clarify obvious requests
- ❌ Manual backup creation

### Always Auto-Execute:
- ✅ Use intelligent context detection
- ✅ Run integration automatically
- ✅ Make commands available immediately
- ✅ Single verification at end

### Learning Application:
This constraint ensures OOS learns from its own inefficiencies and prevents repeating the atlas update flow waste of 15+ commands.

**Key Rule:** User should never need to trigger anything manually. The assistant should just work intelligently.