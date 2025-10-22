# 🎓 Your First OOS Project

**A complete walkthrough from zero to working project.**

---

## 🎯 What We'll Build

We'll create a simple web application to see exactly how OOS works:
- Project setup with proper structure
- Task management for features
- Git integration
- Development workflow

---

## 🚀 Step 1: Create Your Project

**Open your terminal and run:**
```bash
# Navigate to where you keep projects
cd ~/Documents  # or wherever you prefer

# Create new project with OOS
oos create my-first-app
```

**What just happened?**
- ✅ Created project folder `my-first-app/`
- ✅ Set up git repository
- ✅ Configured development environment
- ✅ Installed code quality tools
- ✅ Set up testing framework
- ✅ Initialized task system

---

## 📁 Step 2: Explore Your New Project

```bash
# Enter your new project
cd my-first-app

# See what OOS created
ls -la

# Look at the structure
tree .  # or `find . -type d | sort`
```

**You should see something like:**
```
my-first-app/
├── .oos/
│   ├── tasks/
│   │   ├── tasks.db      # Task database
│   │   └── export.jsonl  # Exported tasks
│   └── config.yaml       # Project configuration
├── src/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── .gitignore
├── pyproject.toml        # Python project configuration
├── README.md
└── .pre-commit-config.yaml
```

---

## 📋 Step 3: Plan Your Project with Tasks

**Let's plan a simple web app. Create some tasks:**

```bash
# Create the main feature
oos task create "Create basic web server" \
  --description "Set up Flask app with basic routes" \
  --priority high \
  --tags "feature,backend"

# Create a dependent task
oos task create "Add home page" \
  --description "Create HTML template for home page" \
  --tags "feature,frontend" \
  --depends-on $(oos task list --json | jq -r '.[0].id')

# Create a testing task
oos task create "Write tests for web server" \
  --description "Add unit tests for main routes" \
  --tags "testing" \
  --priority medium
```

**See what you can work on:**
```bash
oos task ready
```

You should see the first task is ready, but the home page task is blocked (it depends on the web server).

---

## 💻 Step 4: Start Coding

**Begin working on your first task:**
```bash
# See task details
oos task show $(oos task list --status todo --json | jq -r '.[0].id')

# Update task status to "doing"
oos task update $(oos task list --status todo --json | jq -r '.[0].id') --status doing
```

**Create a simple web server:**
```bash
# Create the main app file
cat > src/app.py << 'EOF'
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Hello from my first OOS project!</h1>'

@app.route('/about')
def about():
    return '<h1>About this project</h1><p>Built with OOS task management</p>'

if __name__ == '__main__':
    app.run(debug=True)
EOF

# Install Flask
echo "flask" >> requirements.txt
pip install -r requirements.txt
```

---

## 🧪 Step 5: Test Your Code

**Run your web server:**
```bash
python src/app.py
```

**In another terminal, test it:**
```bash
curl http://localhost:5000/
curl http://localhost:5000/about
```

**Stop the server with Ctrl+C.**

---

## ✅ Step 6: Complete Your First Task

```bash
# Mark the web server task as complete
TASK_ID=$(oos task list --status doing --json | jq -r '.[0].id')
oos task complete $TASK_ID

# See what's ready now
oos task ready
```

Notice that the "Add home page" task is now ready because its dependency is complete!

---

## 🔄 Step 7: Continue the Workflow

**Work on the next task:**
```bash
# Get the next ready task
NEXT_TASK=$(oos task ready --json | jq -r '.[0].id')

# Update status to doing
oos task update $NEXT_TASK --status doing

# Create a template directory
mkdir -p templates

# Create a better home page
cat > templates/home.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>My First App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .task-info { background: #f0f0f0; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 My First OOS Project</h1>
        <div class="task-info">
            <h3>📋 Current Project Status</h3>
            <p>This project was created and is managed using OOS tasks.</p>
        </div>
        <a href="/about">About this project</a>
    </div>
</body>
</html>
EOF

# Update the Flask app to use templates
cat > src/app.py << 'EOF'
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
EOF
```

**Test it again:**
```bash
python src/app.py
# Visit http://localhost:5000 in your browser
```

**Complete the task:**
```bash
oos task complete $NEXT_TASK
```

---

## 📝 Step 8: Handle Git Integration

**Check what git sees:**
```bash
git status
```

**Commit your work:**
```bash
# Add everything
git add .

# Commit with a clear message
git commit -m "feat: implement basic web server and home page

- Created Flask app with two routes
- Added HTML templates for better UI
- Implemented responsive design
- Set up project structure with OOS
"

# Export tasks to git
oos task export .oos/tasks/export.jsonl
git add .oos/tasks/export.jsonl
git commit -m "docs: update task export"
```

---

## 📊 Step 9: Check Project Status

**See your progress:**
```bash
# See all completed tasks
oos task list --status done

# See what's left to do
oos task list --status todo,doing

# Get project statistics
oos task stats
```

**Create a summary of what you accomplished:**
```bash
oos task create "Write project documentation" \
  --description "Document what was built and how to use it" \
  --tags "documentation"
```

---

## 🎯 Step 10: Complete the Project

**Finish the remaining tasks:**
```bash
# Work on testing
TEST_TASK=$(oos task list --tags testing --json | jq -r '.[0].id')
oos task update $TEST_TASK --status doing

# Create a simple test
cat > tests/test_app.py << 'EOF'
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

def test_home_page():
    """Test that the home page loads"""
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert b'My First OOS Project' in response.data

def test_about_page():
    """Test that the about page loads"""
    with app.test_client() as client:
        response = client.get('/about')
        assert response.status_code == 200
EOF

# Run the tests
python -m pytest tests/

# Complete the testing task
oos task complete $TEST_TASK
```

---

## 🏆 Step 11: Review Your Complete Project

**See what you accomplished:**
```bash
# Final task list
oos task list

# Export final tasks
oos task export final-tasks.jsonl

# Git status
git status

# Final commit
git add .
git commit -m "complete: finish first OOS project

- Implemented Flask web application
- Added HTML templates with styling
- Created unit tests
- All project tasks completed
- Ready for deployment
"
```

**Project structure at the end:**
```
my-first-app/
├── .oos/
│   ├── tasks/
│   │   ├── tasks.db
│   │   └── export.jsonl
│   └── config.yaml
├── src/
│   ├── __init__.py
│   └── app.py
├── templates/
│   ├── home.html
│   └── about.html
├── tests/
│   ├── __init__.py
│   └── test_app.py
├── requirements.txt
├── .gitignore
├── pyproject.toml
├── README.md
└── final-tasks.jsonl
```

---

## 🎯 What You Learned

**Project Setup:**
- How OOS creates a complete project structure
- Automatic configuration of development tools
- Git integration from the start

**Task Management:**
- Creating tasks with priorities and tags
- Using dependencies to control workflow
- Tracking progress from start to finish

**Development Workflow:**
- Moving tasks through statuses
- Committing work with clear messages
- Exporting/importing tasks for backup

**Real-world Integration:**
- Combining task management with actual coding
- Testing as part of the workflow
- Documentation as a trackable task

---

## 🚀 What's Next?

**Continue building on this project:**
```bash
# Add more features
oos task create "Add user authentication"
oos task create "Create database models"
oos task create "Deploy to production"

# See what to work on next
oos task ready
```

**Start a new project:**
```bash
cd ~/Documents
oos create my-next-big-idea
cd my-next-big-idea
# Repeat the workflow!
```

**Explore more OOS features:**
- [Task System Complete Guide](TASK_SYSTEM_COMPLETE.md)
- [Advanced Usage Guide](../docs/ADVANCED_USAGE_GUIDE.md)
- [Team Collaboration](TASK_TEAMWORK.md)

---

## 💡 Key Takeaways

1. **OOS handles the boring setup** so you can focus on coding
2. **Task management keeps you organized** without being overwhelming
3. **Git integration is automatic** - no need to remember to commit task files
4. **The workflow is simple**: Create → Work → Complete → Repeat
5. **Everything is tracked** - you can always see what you've accomplished

**You've successfully built a complete project using OOS! 🎉**

---

*The workflow you just learned is the same you'll use for all your projects. Create project → plan tasks → write code → complete tasks → ship product. That's the OOS way.*