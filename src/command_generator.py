#!/usr/bin/env python3
"""
Idea-to-Command Transformation System

Converts mined patterns and ideas from repository analysis into executable
Claude Code slash commands with automatic parameter inference, template
generation, and documentation.
"""

import json
import re
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import yaml


@dataclass
class CommandParameter:
    """Represents a command parameter with type and validation"""
    name: str
    type: str  # string, integer, boolean, array, object
    required: bool = False
    default: Any = None
    description: str = ""
    validation: Optional[Dict[str, Any]] = None


@dataclass
class CommandTemplate:
    """Represents a generated command template"""
    name: str
    description: str
    category: str
    parameters: List[CommandParameter]
    implementation: str
    usage_examples: List[str]
    dependencies: List[str]
    prerequisites: List[str]
    documentation: str
    source_patterns: List[str]


class IdeaToCommandTransformer:
    """Main class for transforming patterns into executable commands"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.command_templates = []
        self.pattern_to_command_map = {}
        self.command_categories = {
            'setup': 'Project initialization and setup',
            'development': 'Development workflow commands',
            'testing': 'Testing and quality assurance',
            'deployment': 'Deployment and operations',
            'documentation': 'Documentation generation',
            'automation': 'Automation and CI/CD',
            'analysis': 'Code analysis and metrics'
        }

    def transform_patterns_to_commands(self, patterns_data: Dict[str, Any]) -> List[CommandTemplate]:
        """Transform repository analysis patterns into command templates"""
        commands = []

        # Extract patterns from analysis data
        architectural_patterns = patterns_data.get('patterns', {}).get('architectural', [])
        workflows = patterns_data.get('workflows', [])
        file_structure = patterns_data.get('file_structure', {})
        documentation = patterns_data.get('documentation', {})

        # Generate commands from architectural patterns
        commands.extend(self._generate_architecture_commands(architectural_patterns))

        # Generate commands from workflows
        commands.extend(self._generate_workflow_commands(workflows))

        # Generate commands from file structure
        commands.extend(self._generate_structure_commands(file_structure))

        # Generate commands from documentation patterns
        commands.extend(self._generate_documentation_commands(documentation))

        # Generate setup commands based on project characteristics
        commands.extend(self._generate_setup_commands(patterns_data))

        return commands

    def _generate_architecture_commands(self, patterns: List[Dict[str, Any]]) -> List[CommandTemplate]:
        """Generate commands based on architectural patterns"""
        commands = []

        for pattern in patterns:
            if pattern['type'] == 'class_pattern':
                command = self._create_class_based_command(pattern)
                commands.append(command)
            elif pattern['type'] == 'function_pattern':
                command = self._create_function_based_command(pattern)
                commands.append(command)

        return commands

    def _generate_workflow_commands(self, workflows: List[Dict[str, Any]]) -> List[CommandTemplate]:
        """Generate commands based on CI/CD workflows"""
        commands = []

        for workflow in workflows:
            if workflow.get('pattern_type') == 'github_actions':
                command = self._create_github_actions_command(workflow)
                commands.append(command)
            elif workflow.get('type') == 'makefile':
                command = self._create_makefile_command(workflow)
                commands.append(command)
            elif workflow.get('type') == 'docker':
                command = self._create_docker_setup_command()
                commands.append(command)

        return commands

    def _generate_structure_commands(self, file_structure: Dict[str, Any]) -> List[CommandTemplate]:
        """Generate commands based on file organization patterns"""
        commands = []

        # Analyze configuration files
        config_files = file_structure.get('configuration_files', [])
        if any('docker' in f.lower() for f in config_files):
            commands.append(self._create_docker_setup_command())

        # Analyze package files
        package_files = file_structure.get('package_files', [])
        if any('package.json' in f for f in package_files):
            commands.append(self._create_npm_setup_command())
        elif any('requirements.txt' in f for f in package_files):
            commands.append(self._create_python_project_command())

        return commands

    def _generate_documentation_commands(self, docs_analysis: Dict[str, Any]) -> List[CommandTemplate]:
        """Generate commands based on documentation patterns"""
        commands = []

        if docs_analysis.get('readme_exists'):
            commands.append(self._create_readme_generator_command())

        if docs_analysis.get('contributing_guide'):
            commands.append(self._create_contributing_template_command())

        return commands

    def _generate_setup_commands(self, patterns_data: Dict[str, Any]) -> List[CommandTemplate]:
        """Generate setup commands based on project characteristics"""
        commands = []

        # Analyze language and create appropriate setup commands
        metadata = patterns_data.get('metadata', {})
        language = metadata.get('language', '').lower()

        if language == 'python':
            commands.append(self._create_python_project_command())
        elif language in ['javascript', 'typescript']:
            commands.append(self._create_nodejs_project_command())
        elif language == 'go':
            commands.append(self._create_go_project_command())

        # Create general setup commands
        commands.extend([
            self._create_git_setup_command(),
            self._create_license_setup_command(),
            self._create_ci_setup_command()
        ])

        return commands

    def _create_class_based_command(self, pattern: Dict[str, Any]) -> CommandTemplate:
        """Create a command based on class patterns"""
        class_name = pattern['name']
        methods = pattern.get('methods', [])

        command_name = f"create-{self._camel_to_kebab(class_name)}"

        return CommandTemplate(
            name=command_name,
            description=f"Create a {class_name} class with standard methods",
            category='development',
            parameters=[
                CommandParameter('class_name', 'string', True, class_name, 'Name of the class'),
                CommandParameter('methods', 'array', False, methods, 'Methods to include'),
                CommandParameter('file_path', 'string', False, None, 'File path for the class')
            ],
            implementation=self._generate_class_implementation(class_name, methods),
            usage_examples=[
                f"/{command_name} --class-name {class_name}",
                f"/{command_name} --class-name {class_name} --methods save,load,validate"
            ],
            dependencies=['black', 'flake8'],
            prerequisites=['Python project initialized'],
            documentation=f"Creates a {class_name} class with common methods: {', '.join(methods)}",
            source_patterns=[pattern['type']]
        )

    def _create_function_based_command(self, pattern: Dict[str, Any]) -> CommandTemplate:
        """Create a command based on function patterns"""
        function_name = pattern['name']
        args = pattern.get('args', [])

        command_name = f"create-{self._camel_to_kebab(function_name)}-function"

        return CommandTemplate(
            name=command_name,
            description=f"Create a {function_name} function with standard parameters",
            category='development',
            parameters=[
                CommandParameter('function_name', 'string', True, function_name, 'Name of the function'),
                CommandParameter('parameters', 'array', False, args, 'Function parameters'),
                CommandParameter('return_type', 'string', False, None, 'Return type annotation'),
                CommandParameter('file_path', 'string', False, None, 'File path for the function')
            ],
            implementation=self._generate_function_implementation(function_name, args),
            usage_examples=[
                f"/{command_name} --function-name {function_name}",
                f"/{command_name} --function-name {function_name} --parameters data,config"
            ],
            dependencies=['black'],
            prerequisites=['Python project'],
            documentation=f"Creates a {function_name} function with parameters: {', '.join(args)}",
            source_patterns=[pattern['type']]
        )

    def _create_github_actions_command(self, workflow: Dict[str, Any]) -> CommandTemplate:
        """Create a command for GitHub Actions workflow setup"""
        workflow_name = workflow.get('name', 'workflow')

        return CommandTemplate(
            name='setup-github-actions',
            description='Set up GitHub Actions CI/CD pipeline',
            category='automation',
            parameters=[
                CommandParameter('workflow_name', 'string', False, 'ci', 'Name of the workflow'),
                CommandParameter('python_versions', 'array', False, ['3.9', '3.10', '3.11'], 'Python versions to test'),
                CommandParameter('test_command', 'string', False, 'pytest', 'Test command to run'),
                CommandParameter('deploy', 'boolean', False, False, 'Include deployment steps')
            ],
            implementation=self._generate_github_actions_implementation(),
            usage_examples=[
                '/setup-github-actions --workflow-name ci --python-versions 3.9,3.10,3.11',
                '/setup-github-actions --deploy'
            ],
            dependencies=['github-actions'],
            prerequisites=['GitHub repository'],
            documentation='Creates a comprehensive GitHub Actions workflow with testing and optional deployment',
            source_patterns=['github_actions']
        )

    def _create_docker_setup_command(self) -> CommandTemplate:
        """Create a command for Docker setup"""
        return CommandTemplate(
            name='setup-docker',
            description='Add Docker containerization to the project',
            category='deployment',
            parameters=[
                CommandParameter('base_image', 'string', False, 'python:3.11-slim', 'Base Docker image'),
                CommandParameter('port', 'integer', False, 8000, 'Exposed port'),
                CommandParameter('include_compose', 'boolean', False, True, 'Include Docker Compose')
            ],
            implementation=self._generate_docker_implementation(),
            usage_examples=[
                '/setup-docker --base-image python:3.11-slim --port 8000',
                '/setup-docker --include-compose'
            ],
            dependencies=['docker'],
            prerequisites=['Docker installed'],
            documentation='Creates Dockerfile and optionally docker-compose.yml for the project',
            source_patterns=['docker']
        )

    def _create_python_project_command(self) -> CommandTemplate:
        """Create a command for Python project setup"""
        return CommandTemplate(
            name='setup-python-project',
            description='Initialize a new Python project with standard structure',
            category='setup',
            parameters=[
                CommandParameter('project_name', 'string', True, None, 'Name of the project'),
                CommandParameter('venv_name', 'string', False, 'venv', 'Virtual environment name'),
                CommandParameter('python_version', 'string', False, '3.11', 'Python version'),
                CommandParameter('include_tests', 'boolean', False, True, 'Include test structure'),
                CommandParameter('include_docs', 'boolean', False, True, 'Include documentation structure')
            ],
            implementation=self._generate_python_project_implementation(),
            usage_examples=[
                '/setup-python-project --project-name my-app --python-version 3.11',
                '/setup-python-project --project-name my-app --include-tests --include-docs'
            ],
            dependencies=['pip', 'setuptools'],
            prerequisites=['Python installed'],
            documentation='Creates a complete Python project structure with virtual environment, requirements, and standard directories',
            source_patterns=['python_setup']
        )

    def _create_nodejs_project_command(self) -> CommandTemplate:
        """Create a command for Node.js project setup"""
        return CommandTemplate(
            name='setup-nodejs-project',
            description='Initialize a new Node.js project with standard structure',
            category='setup',
            parameters=[
                CommandParameter('project_name', 'string', True, None, 'Name of the project'),
                CommandParameter('node_version', 'string', False, '18', 'Node.js version'),
                CommandParameter('package_manager', 'string', False, 'npm', 'Package manager (npm/yarn/pnpm)'),
                CommandParameter('include_typescript', 'boolean', False, False, 'Include TypeScript setup'),
                CommandParameter('include_tests', 'boolean', False, True, 'Include test structure')
            ],
            implementation=self._generate_nodejs_project_implementation(),
            usage_examples=[
                '/setup-nodejs-project --project-name my-app --node-version 18',
                '/setup-nodejs-project --project-name my-app --include-typescript --include-tests'
            ],
            dependencies=['node', 'npm'],
            prerequisites=['Node.js installed'],
            documentation='Creates a complete Node.js project structure with package.json and standard directories',
            source_patterns=['nodejs_setup']
        )

    def _create_go_project_command(self) -> CommandTemplate:
        """Create Go project setup command"""
        return CommandTemplate(
            name='setup-go-project',
            description='Initialize a new Go project with standard structure',
            category='setup',
            parameters=[
                CommandParameter('project_name', 'string', True, None, 'Name of the project'),
                CommandParameter('go_version', 'string', False, '1.21', 'Go version'),
                CommandParameter('module_name', 'string', False, None, 'Go module name (defaults to project name)'),
                CommandParameter('include_tests', 'boolean', False, True, 'Include test structure')
            ],
            implementation=self._generate_go_project_implementation(),
            usage_examples=[
                '/setup-go-project --project-name my-app --go-version 1.21',
                '/setup-go-project --project-name my-service --module-name github.com/user/my-service'
            ],
            dependencies=['go'],
            prerequisites=['Go installed'],
            documentation='Creates a complete Go project with proper module structure, standard directory layout, and best practices',
            source_patterns=['go_setup']
        )

    def _create_npm_setup_command(self) -> CommandTemplate:
        """Create a command for NPM project setup"""
        return CommandTemplate(
            name='setup-npm-project',
            description='Initialize NPM project structure',
            category='setup',
            parameters=[
                CommandParameter('project_name', 'string', True, None, 'Name of the project'),
                CommandParameter('package_manager', 'string', False, 'npm', 'Package manager'),
                CommandParameter('include_tests', 'boolean', False, True, 'Include test structure')
            ],
            implementation=self._generate_npm_setup_implementation(),
            usage_examples=[
                '/setup-npm-project --project-name my-app',
                '/setup-npm-project --project-name my-app --include-tests'
            ],
            dependencies=['npm'],
            prerequisites=['Node.js installed'],
            documentation='Creates NPM project structure with package.json',
            source_patterns=['npm_setup']
        )

    def _create_makefile_command(self, workflow: Dict[str, Any]) -> CommandTemplate:
        """Create a command for Makefile setup"""
        return CommandTemplate(
            name='setup-makefile',
            description='Create a Makefile for project automation',
            category='automation',
            parameters=[
                CommandParameter('targets', 'array', False, ['build', 'test', 'clean'], 'Makefile targets'),
                CommandParameter('include_install', 'boolean', False, True, 'Include install target')
            ],
            implementation=self._generate_makefile_implementation(),
            usage_examples=[
                '/setup-makefile --targets build,test,clean',
                '/setup-makefile --include-install'
            ],
            dependencies=['make'],
            prerequisites=['Unix-like system'],
            documentation='Creates a Makefile with common build targets',
            source_patterns=['makefile']
        )

    def _create_readme_generator_command(self) -> CommandTemplate:
        """Create a command for README generation"""
        return CommandTemplate(
            name='generate-readme',
            description='Generate a comprehensive README file',
            category='documentation',
            parameters=[
                CommandParameter('project_name', 'string', True, None, 'Name of the project'),
                CommandParameter('description', 'string', False, None, 'Project description'),
                CommandParameter('include_installation', 'boolean', False, True, 'Include installation section'),
                CommandParameter('include_usage', 'boolean', False, True, 'Include usage section')
            ],
            implementation=self._generate_readme_implementation(),
            usage_examples=[
                '/generate-readme --project-name my-app --description "My awesome app"',
                '/generate-readme --project-name my-app --include-installation --include-usage'
            ],
            dependencies=[],
            prerequisites=[],
            documentation='Generates a comprehensive README.md file',
            source_patterns=['documentation']
        )

    def _create_contributing_template_command(self) -> CommandTemplate:
        """Create a command for contributing guide template"""
        return CommandTemplate(
            name='create-contributing-guide',
            description='Create a contributing guide template',
            category='documentation',
            parameters=[
                CommandParameter('project_name', 'string', False, None, 'Name of the project'),
                CommandParameter('include_coc', 'boolean', False, True, 'Include code of conduct')
            ],
            implementation=self._generate_contributing_implementation(),
            usage_examples=[
                '/create-contributing-guide --project-name my-app',
                '/create-contributing-guide --project-name my-app --include-coc'
            ],
            dependencies=[],
            prerequisites=[],
            documentation='Creates a CONTRIBUTING.md template',
            source_patterns=['documentation']
        )

    def _create_git_setup_command(self) -> CommandTemplate:
        """Create a command for Git repository setup"""
        return CommandTemplate(
            name='setup-git-repository',
            description='Initialize Git repository with standard setup',
            category='setup',
            parameters=[
                CommandParameter('repo_name', 'string', True, None, 'Repository name'),
                CommandParameter('include_github', 'boolean', False, True, 'Include GitHub remote setup'),
                CommandParameter('default_branch', 'string', False, 'main', 'Default branch name')
            ],
            implementation=self._generate_git_setup_implementation(),
            usage_examples=[
                '/setup-git-repository --repo-name my-project',
                '/setup-git-repository --repo-name my-project --include-github'
            ],
            dependencies=['git'],
            prerequisites=['Git installed'],
            documentation='Initializes Git repository with standard configuration',
            source_patterns=['git_setup']
        )

    def _create_license_setup_command(self) -> CommandTemplate:
        """Create a command for license setup"""
        return CommandTemplate(
            name='setup-license',
            description='Add a license file to the project',
            category='setup',
            parameters=[
                CommandParameter('license_type', 'string', False, 'MIT', 'Type of license'),
                CommandParameter('author_name', 'string', False, None, 'Author name'),
                CommandParameter('author_email', 'string', False, None, 'Author email')
            ],
            implementation=self._generate_license_implementation(),
            usage_examples=[
                '/setup-license --license-type MIT --author-name "Your Name"',
                '/setup-license --license-type Apache-2.0'
            ],
            dependencies=[],
            prerequisites=[],
            documentation='Creates a license file based on the selected license type',
            source_patterns=['license_setup']
        )

    def _create_ci_setup_command(self) -> CommandTemplate:
        """Create a command for CI/CD setup"""
        return CommandTemplate(
            name='setup-ci-cd',
            description='Set up basic CI/CD pipeline',
            category='automation',
            parameters=[
                CommandParameter('platform', 'string', False, 'github', 'CI/CD platform (github/gitlab)'),
                CommandParameter('language', 'string', False, 'python', 'Primary language'),
                CommandParameter('include_deployment', 'boolean', False, False, 'Include deployment steps')
            ],
            implementation=self._generate_ci_implementation(),
            usage_examples=[
                '/setup-ci-cd --platform github --language python',
                '/setup-ci-cd --platform gitlab --include-deployment'
            ],
            dependencies=[],
            prerequisites=[],
            documentation='Sets up a basic CI/CD pipeline configuration',
            source_patterns=['ci_setup']
        )

    def _generate_npm_setup_implementation(self) -> str:
        """Generate NPM setup implementation"""
        return '''# Initialize NPM project
{{package_manager}} init -y

# Create basic structure
mkdir -p src tests docs

# Create basic files
cat > src/index.js << EOF
/**
 * {{project_name}} main module
 */

function main() {
    console.log('{{project_name}} is running!');
}

module.exports = { main };
EOF

# Update package.json
{{package_manager}} install --save-dev {{#include_tests}}jest{{/include_tests}}

echo "NPM project '{{project_name}}' created successfully!"'''

    def _generate_makefile_implementation(self) -> str:
        """Generate Makefile implementation"""
        return '''# Makefile for {{project_name}}

.PHONY: help build test clean install

help:
\t@echo "Available targets:"
\t@echo "  build     - Build the project"
\t@echo "  test      - Run tests"
\t@echo "  clean     - Clean build artifacts"
\t{{#include_install}}\t@echo "  install   - Install dependencies"{{/include_install}}

build:
\t# Add build commands here
\t@echo "Building project..."

test:
\t# Add test commands here
\t@echo "Running tests..."

clean:
\t# Add clean commands here
\t@echo "Cleaning build artifacts..."

{{#include_install}}install:
\t# Add install commands here
\t@echo "Installing dependencies..."{{/include_install}}'''

    def _generate_readme_implementation(self) -> str:
        """Generate README implementation"""
        return """# {{project_name}}

{{#description}}{{description}}{{/description}}{{^description}}{{project_name}} project description.{{/description}}

## Installation

{{#include_installation}}
```bash
# Add installation instructions here
```
{{/include_installation}}

## Usage

{{#include_usage}}
```bash
# Add usage instructions here
```
{{/include_usage}}

## Development

{{#include_installation}}
```bash
# Add development setup here
```
{{/include_installation}}

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""

    def _generate_contributing_implementation(self) -> str:
        """Generate contributing guide implementation"""
        return '''# Contributing to {{#project_name}}{{project_name}}{{/project_name}}{{^project_name}}this project{{/project_name}}

We love your input! We want to make contributing to {{#project_name}}{{project_name}}{{/project_name}}{{^project_name}}this project{{/project_name}} as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, document issues, track features, and accept pull requests.

## Pull Request Process

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

{{#include_coc}}
## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).
{{/include_coc}}

## License

By contributing, you agree that your contributions will be licensed under the project's license.
'''

    def _generate_git_setup_implementation(self) -> str:
        """Generate Git setup implementation"""
        return '''# Initialize Git repository
git init

# Set default branch name
git branch -m {{default_branch}}

# Create basic .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF

# Create initial commit
git add .
git commit -m "Initial commit: Project setup"

{{#include_github}}
# Setup GitHub remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/{{repo_name}}.git
git push -u origin {{default_branch}}
{{/include_github}}

echo "Git repository initialized successfully!"'''

    def _generate_license_implementation(self) -> str:
        """Generate license implementation"""
        return '''# License file generation would go here
# This would generate the appropriate license text based on the license_type
# For now, creating a placeholder

cat > LICENSE << EOF
{{license_type}} License

Copyright (c) {{current_year}} {{#author_name}}{{author_name}}{{/author_name}}{{^author_name}}The Author{{/author_name}}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

echo "License file created!"'''

    def _generate_ci_implementation(self) -> str:
        """Generate CI implementation"""
        return '''# CI/CD setup would go here
# This would generate appropriate CI/CD configuration based on the platform

if [ "{{platform}}" = "github" ]; then
    # Create GitHub Actions workflow
    mkdir -p .github/workflows

    cat > .github/workflows/ci.yml << EOF
name: CI

on:
  push:
    branches: [ {{default_branch}} ]
  pull_request:
    branches: [ {{default_branch}} ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up {{language}}
      uses: actions/setup-{{language}}@v4
      with:
        {{language}}-version: 'latest'

    - name: Install dependencies
      run: |
        # Add dependency installation commands here

    - name: Run tests
      run: |
        # Add test commands here

{{#include_deployment}}
  deploy:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/{{default_branch}}'

    steps:
    - uses: actions/checkout@v3

    - name: Deploy
      run: |
        # Add deployment commands here
{{/include_deployment}}
EOF

    echo "GitHub Actions CI workflow created!"
elif [ "{{platform}}" = "gitlab" ]; then
    # Create GitLab CI configuration
    cat > .gitlab-ci.yml << EOF
stages:
  - test
  {{#include_deployment}}- deploy{{/include_deployment}}

test:
  stage: test
  script:
    # Add test commands here
  only:
    - {{default_branch}}

{{#include_deployment}}
deploy:
  stage: deploy
  script:
    # Add deployment commands here
  only:
    - {{default_branch}}
{{/include_deployment}}
EOF

    echo "GitLab CI configuration created!"
fi

echo "CI/CD setup completed!"'''

    def _generate_class_implementation(self, class_name: str, methods: List[str]) -> str:
        """Generate Python class implementation template"""
        method_templates = []
        for method in methods:
            method_templates.append(f"""
    def {method}(self):
        \"\"\"{method} method\"\"\"
        pass""")

        return f'''class {class_name}:
    \"\"\"{class_name} class\"\"\"

    def __init__(self):
        \"\"\"Initialize {class_name}\"\"\"
        pass{"".join(method_templates)}'''

    def _generate_function_implementation(self, function_name: str, args: List[str]) -> str:
        """Generate Python function implementation template"""
        args_str = ', '.join(args) if args else ''
        return f'''def {function_name}({args_str}):
    \"\"\"{function_name} function\"\"\"
    pass'''

    def _generate_github_actions_implementation(self) -> str:
        """Generate GitHub Actions workflow implementation"""
        return '''name: {{workflow_name}}

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: {{python_versions}}

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{{ matrix.python-version }}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{ matrix.python-version }}}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: {{test_command}}

    - name: Lint code
      run: |
        flake8 .
        black --check .'''

    def _generate_docker_implementation(self) -> str:
        """Generate Docker implementation template"""
        return '''FROM {{base_image}}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {{port}}

CMD ["python", "main.py"]'''

    def _generate_python_project_implementation(self) -> str:
        """Generate Python project setup implementation"""
        return """# Create virtual environment
python -m venv {{venv_name}}

# Activate virtual environment
source {{venv_name}}/bin/activate

# Create project structure
mkdir -p {{project_name}}/{{project_name}} tests docs

# Create initial files
cd {{project_name}}

# Create setup.py
cat > setup.py << EOF
from setuptools import setup, find_packages

setup(
    name=\"{{project_name}}\",
    version=\"0.1.0\",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
    ],
    author=\"Your Name\",
    description=\"{{project_name}} project\",
)
EOF

# Create requirements.txt
cat > requirements.txt << EOF
# Add your requirements here
EOF

# Create main module
cat > {{project_name}}/__init__.py << EOF
\"\"\"{{project_name}} module\"\"\"

__version__ = \"0.1.0\"
EOF

# Create main.py
cat > {{project_name}}/main.py << EOF
\"\"\"Main module for {{project_name}}\"\"\"

def main():
    print(\"{{project_name}} is running!\")

if __name__ == \"__main__\":
    main()
EOF

# Create test file
if {{include_tests}}:
    cat > tests/test_main.py << EOF
\"\"\"Tests for {{project_name}}\"\"\"

import unittest
from {{project_name}}.main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        # Add your tests here
        pass

if __name__ == \"__main__\":
    unittest.main()
EOF

# Create README
cat > README.md << EOF
# {{project_name}}

{{project_name}} project description.

## Installation

```bash
pip install -e .
```

## Usage

```bash
python -m {{project_name}}
```
EOF

echo \"Python project '{{project_name}}' created successfully!\""""

    def _generate_nodejs_project_implementation(self) -> str:
        """Generate Node.js project setup implementation"""
        return '''# Create project directory and initialize
mkdir {{project_name}} && cd {{project_name}}

# Initialize Node.js project
{{package_manager}} init -y

# Create project structure
mkdir -p src tests docs

# Create main entry point
cat > src/index.js << EOF
/**
 * {{project_name}} main module
 */

function main() {
    console.log('{{project_name}} is running!');
}

if (require.main === module) {
    main();
}

module.exports = { main };
EOF

# Create package.json updates
{{package_manager}} install --save-dev {{#include_typescript}}typescript @types/node ts-node{{/include_typescript}} {{#include_tests}}jest{{/include_tests}}

# Create test file
if {{include_tests}}:
    cat > tests/index.test.js << EOF
/**
 * Tests for {{project_name}}
 */

const { main } = require('../src/index');

describe('main', () => {
    test('should run without errors', () => {
        expect(() => main()).not.toThrow();
    });
});
EOF

# Create README
cat > README.md << EOF
# {{project_name}}

{{project_name}} project description.

## Installation

```bash
{{package_manager}} install
```

## Usage

```bash
{{package_manager}} start
```

## Development

```bash
{{package_manager}} test
```
EOF

echo "Node.js project '{{project_name}}' created successfully!"'''

    def _generate_go_project_implementation(self) -> str:
        """Generate Go project implementation template"""
        return '''#!/bin/bash
set -e

PROJECT_NAME="{{project_name}}"
GO_VERSION="{{go_version}}"
MODULE_NAME="${{module_name:-$PROJECT_NAME}}"
INCLUDE_TESTS="{{include_tests}}"

echo "🚀 Setting up Go project: $PROJECT_NAME"

# Create project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Initialize Go module
go mod init "$MODULE_NAME"

# Create standard Go project structure
mkdir -p cmd/$PROJECT_NAME internal/{config,service} pkg/{api,model}

# Create main.go
cat > cmd/$PROJECT_NAME/main.go << EOF
package main

import (
	"fmt"
	"log"
)

func main() {
	fmt.Println("Hello from $PROJECT_NAME!")

	// Add your application logic here
	if err := run(); err != nil {
		log.Fatal(err)
	}
}

func run() error {
	// TODO: Implement your application logic
	return nil
}
EOF

# Create internal/config/config.go
cat > internal/config/config.go << EOF
package config

import (
	"os"
)

type Config struct {
	// Add your configuration fields here
}

func Load() (*Config, error) {
	// TODO: Load configuration from environment or files
	return &Config{}, nil
}
EOF

# Create .gitignore
cat > .gitignore << EOF
# Binaries for programs and plugins
*.exe
*.exe~
*.dll
*.so
*.dylib
$PROJECT_NAME

# Test binary, built with 'go test -c'
*.test

# Output of the go coverage tool
*.out

# Go workspace file
go.work

# Dependency directories
vendor/

# IDE specific files
.idea/
.vscode/
*.swp
*.swo
*~
EOF

# Create test structure if requested
if [ "$INCLUDE_TESTS" = "true" ]; then
    mkdir -p tests
    cat > tests/main_test.go << EOF
package main

import (
	"testing"
)

func TestMain(t *testing.T) {
	// TODO: Add your tests here
}
EOF
fi

# Create README.md
cat > README.md << EOF
# $PROJECT_NAME

A Go project built with best practices.

## Getting Started

```bash
# Clone and navigate to the project
cd $PROJECT_NAME

# Download dependencies
go mod tidy

# Run the application
go run cmd/$PROJECT_NAME/main.go

# Build the application
go build -o $PROJECT_NAME cmd/$PROJECT_NAME/main.go

# Run tests
go test ./...
```
EOF

echo "✅ Go project '$PROJECT_NAME' created successfully!"
echo "📦 Run 'cd $PROJECT_NAME && go mod tidy' to download dependencies"
echo "🏃‍♂️ Run 'go run cmd/$PROJECT_NAME/main.go' to start the application"'''

    def _camel_to_kebab(self, text: str) -> str:
        """Convert camelCase to kebab-case and also convert underscores to hyphens"""
        # First convert underscores to hyphens
        text = text.replace('_', '-')
        # Then convert camelCase to kebab-case
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', text).lower()

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    def save_commands(self, commands: List[CommandTemplate], output_path: str):
        """Save generated commands to file"""
        commands_data = [asdict(cmd) for cmd in commands]

        with open(output_path, 'w') as f:
            json.dump(commands_data, f, indent=2)

    def generate_command_library(self, patterns_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete command library from patterns"""
        commands = self.transform_patterns_to_commands(patterns_data)

        library = {
            'metadata': {
                'total_commands': len(commands),
                'categories': {cat: len([c for c in commands if c.category == cat])
                              for cat in self.command_categories.keys()},
                'generated_at': str(uuid.uuid4())
            },
            'commands': [asdict(cmd) for cmd in commands],
            'usage_guide': self._generate_usage_guide(commands)
        }

        return library

    def generate_claude_code_commands(self, patterns_data: Dict[str, Any], output_dir: str = ".claude/commands") -> None:
        """Generate Claude Code compatible markdown slash commands"""
        commands = self.transform_patterns_to_commands(patterns_data)

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Generate markdown file for each command
        for cmd in commands:
            self._create_claude_command_file(cmd, output_dir)

    def _create_claude_command_file(self, cmd: CommandTemplate, output_dir: str) -> None:
        """Create a single Claude Code command markdown file"""
        # Clean command name for filename
        filename = cmd.name.replace('_', '-').replace(' ', '-').lower()
        filepath = Path(output_dir) / f"{filename}.md"

        # Build frontmatter
        frontmatter = [
            "---",
            f'description: "{cmd.description}"',
            'tools: ["Bash"]',
            "---",
            ""
        ]

        # Build content
        content = [
            cmd.description,
            "",
            "```bash"
        ]

        # Add implementation with parameter substitution
        implementation = cmd.implementation
        if cmd.parameters:
            # Replace parameter placeholders with $ARGUMENTS or specific $1, $2, etc.
            for i, param in enumerate(cmd.parameters, 1):
                param_placeholder = f"{{{{param.name}}}}"
                if param_placeholder in implementation:
                    implementation = implementation.replace(param_placeholder, f"${i}")

            # If no specific parameters found, use $ARGUMENTS
            if "$" not in implementation:
                implementation += " $ARGUMENTS"

        content.extend([
            implementation,
            "```"
        ])

        # Add usage examples if available
        if cmd.usage_examples:
            content.extend([
                "",
                "## Examples:",
                ""
            ])
            for example in cmd.usage_examples:
                content.append(f"- `{example}`")

        # Write file
        full_content = "\n".join(frontmatter + content)
        filepath.write_text(full_content)

    def _generate_usage_guide(self, commands: List[CommandTemplate]) -> Dict[str, Any]:
        """Generate usage guide for commands"""
        guide = {
            'introduction': 'This library contains Claude Code slash commands generated from your development patterns.',
            'categories': {},
            'examples': []
        }

        # Group commands by category
        for category, description in self.command_categories.items():
            category_commands = [cmd for cmd in commands if cmd.category == category]
            guide['categories'][category] = {
                'description': description,
                'commands': [{'name': cmd.name, 'description': cmd.description}
                           for cmd in category_commands]
            }

        # Add examples
        guide['examples'] = [
            {
                'pattern': 'Python project setup',
                'commands': ['/setup-python-project --project-name my-app'],
                'description': 'Initialize a new Python project'
            },
            {
                'pattern': 'Docker containerization',
                'commands': ['/setup-docker --base-image python:3.11-slim'],
                'description': 'Add Docker support to existing project'
            }
        ]

        return guide


def main():
    """Main function for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Idea-to-Command Transformation System')
    parser.add_argument('patterns_file', help='JSON file with repository patterns')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['json', 'yaml'], default='json', help='Output format')
    parser.add_argument('--config', '-c', help='Configuration file path')

    args = parser.parse_args()

    transformer = IdeaToCommandTransformer(args.config)

    try:
        # Load patterns data
        with open(args.patterns_file, 'r') as f:
            patterns_data = json.load(f)

        # Generate command library
        library = transformer.generate_command_library(patterns_data)

        # Save output
        if args.format == 'yaml':
            with open(args.output or 'commands.yaml', 'w') as f:
                yaml.dump(library, f, default_flow_style=False, indent=2)
        else:
            with open(args.output or 'commands.json', 'w') as f:
                json.dump(library, f, indent=2)

        print(f"Generated {library['metadata']['total_commands']} commands")
        if args.output:
            print(f"Commands saved to {args.output}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())