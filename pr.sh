#!/bin/bash

# Script para generar un prompt de análisis de PR basado en el diff con main/master

# Determinar si la rama principal es 'main' o 'master'
MAIN_BRANCH="main"
if ! git show-ref --verify --quiet refs/heads/main; then
  if git show-ref --verify --quiet refs/heads/master; then
    MAIN_BRANCH="master"
  else
    echo "Error: Neither 'main' nor 'master' branch found."
    exit 1
  fi
fi

# Obtener la rama actual
CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" == "$MAIN_BRANCH" ]; then
  echo "Error: You are currently on the $MAIN_BRANCH branch. Please checkout a feature branch."
  exit 1
fi

# Obtener el diff
DIFF=$(git diff $MAIN_BRANCH..$CURRENT_BRANCH)

# Generar el prompt
PROMPT="# Pull Request Analysis Request

Please analyze the following Git diff from a pull request and provide a detailed contribution analysis in English.

## Expected Analysis Structure

1. **Summary of Changes**
   - Brief overview of the main modifications
   - Key components affected

2. **Technical Details**
   - Files modified/added/deleted
   - Key functions or methods changed
   - Code quality observations

3. **Implementation Analysis**
   - Approach taken
   - Design patterns used
   - Potential improvements

4. **Testing Considerations**
   - Tests added/modified
   - Test coverage
   - Areas that might need additional testing

5. **Documentation**
   - Documentation quality
   - Areas that might need more documentation

6. **Impact Assessment**
   - Potential impact on existing functionality
   - Performance considerations
   - Security implications (if any)

7. **Conclusion**
   - Overall assessment of the PR
   - Recommendations (approve, request changes, etc.)

## Git Diff

\`\`\`diff
$DIFF
\`\`\`
"

# Imprimir el prompt o guardarlo en un archivo
if [ -n "$1" ]; then
  echo "$PROMPT" > "$1"
  echo "Prompt saved to $1"
else
  echo "$PROMPT"
fi
