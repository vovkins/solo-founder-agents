#!/usr/bin/env python3
"""Initialize React Native project in GitHub repository."""

import json
import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.github_tools import create_file_in_repo


def create_react_native_project() -> dict:
    """Create React Native project structure in GitHub.
    
    Returns:
        Dictionary with creation results
    """
    results = {"created": [], "errors": []}
    
    # 1. package.json
    package_json = {
        "name": "task-management-app",
        "version": "0.0.1",
        "private": True,
        "scripts": {
            "android": "react-native run-android",
            "ios": "react-native run-ios",
            "start": "react-native start",
            "test": "jest",
            "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
            "type-check": "tsc --noEmit",
        },
        "dependencies": {
            "react": "18.2.0",
            "react-native": "0.73.6",
        },
        "devDependencies": {
            "@babel/core": "^7.24.0",
            "@babel/preset-env": "^7.24.0",
            "@babel/runtime": "^7.24.0",
            "@react-native/babel-preset": "0.73.19",
            "@react-native/eslint-config": "0.73.2",
            "@react-native/metro-config": "0.73.3",
            "@react-native/typescript-config": "0.73.1",
            "@types/react": "^18.2.0",
            "@types/react-native": "^0.73.0",
            "@typescript-eslint/eslint-plugin": "^7.0.0",
            "@typescript-eslint/parser": "^7.0.0",
            "eslint": "^8.57.0",
            "eslint-config-prettier": "^9.1.0",
            "eslint-plugin-react": "^7.34.0",
            "eslint-plugin-react-hooks": "^4.6.0",
            "prettier": "^3.2.0",
            "typescript": "^5.4.0",
        },
        "engines": {
            "node": ">=18"
        }
    }
    
    # 2. tsconfig.json
    tsconfig = {
        "compilerOptions": {
            "target": "esnext",
            "module": "commonjs",
            "lib": ["es2017"],
            "allowJs": True,
            "jsx": "react-native",
            "noEmit": True,
            "isolatedModules": True,
            "strict": True,
            "moduleResolution": "node",
            "baseUrl": "./",
            "paths": {
                "@/*": ["src/*"],
                "@components/*": ["src/components/*"],
                "@screens/*": ["src/screens/*"],
                "@utils/*": ["src/utils/*"],
                "@api/*": ["src/api/*"],
                "@types/*": ["src/types/*"],
            },
            "allowSyntheticDefaultImports": True,
            "esModuleInterop": True,
            "skipLibCheck": True,
            "resolveJsonModule": True,
            "forceConsistentCasingInFileNames": True,
        },
        "include": ["src/**/*", "index.js", "App.tsx"],
        "exclude": ["node_modules", "babel.config.js", "metro.config.js"]
    }
    
    # 3. .eslintrc.js
    eslintrc = '''module.exports = {
  root: true,
  extends: [
    '@react-native',
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'prettier',
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'react', 'react-hooks'],
  parserOptions: {
    ecmaVersion: 2021,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  rules: {
    'react/react-in-jsx-scope': 'off',
    'react/prop-types': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
'''
    
    # 4. .prettierrc
    prettierrc = {
        "semi": True,
        "trailingComma": "es5",
        "singleQuote": True,
        "printWidth": 100,
        "tabWidth": 2,
        "useTabs": False,
    }
    
    # 5. .gitignore
    gitignore = '''# OSX
.DS_Store

# Xcode
build/
*.pbxuser
!default.pbxuser
*.mode1v3
!default.mode1v3
*.mode2v3
!default.mode2v3
*.perspectivev3
!default.perspectivev3
xcuserdata
*.xccheckout
*.moved-aside
DerivedData
*.hmap
*.ipa
*.xcuserstate
ios/.xcode.env.local

# Android/IntelliJ
build/
.idea
.gradle
local.properties
*.iml
*.hprof
.cxx/
*.keystore
!debug.keystore

# Node
node_modules/
*.log
.npm

# BUCK
buck-out/
\\.buckd/
*.keystore

# Bundle artifacts
*.jsbundle

# CocoaPods
ios/Pods/

# Environment
.env
.env.local
.env.*.local

# Testing
coverage/

# TypeScript
*.tsbuildinfo

# Editor
.vscode/
*.swp
*.swo
'''
    
    # 6. babel.config.js
    babel_config = '''module.exports = {
  presets: ['module:@react-native/babel-preset'],
};
'''
    
    # 7. metro.config.js
    metro_config = '''const {getDefaultConfig, mergeConfig} = require('@react-native/metro-config');

/**
 * Metro configuration
 * https://reactnative.dev/docs/metro
 *
 * @type {import('metro-config').MetroConfig}
 */
const config = {};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);
'''
    
    # 8. App.tsx
    app_tsx = '''import React from 'react';
import {SafeAreaView, StyleSheet, Text, View} from 'react-native';

function App(): React.JSX.Element {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Welcome to Task Management App</Text>
        <Text style={styles.subtitle}>React Native + TypeScript</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1e40af',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
  },
});

export default App;
'''
    
    # 9. index.js
    index_js = '''import {AppRegistry} from 'react-native';
import App from './App';
import {name as appName} from './app.json';

AppRegistry.registerComponent(appName, () => App);
'''
    
    # 10. app.json
    app_json = {
        "name": "TaskManagementApp",
        "displayName": "Task Management"
    }
    
    # 11. README.md
    readme = '''# Task Management App

React Native application for task management, built with TypeScript.

## Tech Stack

- React Native 0.73
- TypeScript 5.4
- ESLint + Prettier

## Getting Started

```bash
# Install dependencies
npm install

# iOS
npm run ios

# Android
npm run android
```

## Project Structure

```
src/
├── api/          # API client and services
├── components/   # Reusable UI components
├── screens/      # Screen components
├── types/        # TypeScript type definitions
└── utils/        # Utility functions
```

## Scripts

- `npm start` - Start Metro bundler
- `npm run ios` - Run on iOS
- `npm run android` - Run on Android
- `npm test` - Run tests
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript check
'''
    
    # 12. src/types/index.ts
    types_index = '''/**
 * Common type definitions for the application
 */

export type Status = 'pending' | 'in_progress' | 'completed' | 'cancelled';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: Status;
  createdAt: Date;
  updatedAt: Date;
}

export interface User {
  id: string;
  name: string;
  email: string;
}
'''
    
    # 13. src/utils/index.ts
    utils_index = '''/**
 * Utility functions
 */

export const formatDate = (date: Date): string => {
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const generateId = (): string => {
  return Math.random().toString(36).substring(2, 9);
};
'''
    
    # Files to create
    files = [
        ("package.json", json.dumps(package_json, indent=2)),
        ("tsconfig.json", json.dumps(tsconfig, indent=2)),
        (".eslintrc.js", eslintrc),
        (".prettierrc", json.dumps(prettierrc, indent=2)),
        (".gitignore", gitignore),
        ("babel.config.js", babel_config),
        ("metro.config.js", metro_config),
        ("App.tsx", app_tsx),
        ("index.js", index_js),
        ("app.json", json.dumps(app_json, indent=2)),
        ("README.md", readme),
        ("src/types/index.ts", types_index),
        ("src/utils/index.ts", utils_index),
        ("src/components/.gitkeep", "# Components directory"),
        ("src/screens/.gitkeep", "# Screens directory"),
        ("src/api/.gitkeep", "# API directory"),
    ]
    
    for path, content in files:
        try:
            url = create_file_in_repo(
                path=path,
                content=content,
                message=f"feat: Initialize React Native project - add {path}",
            )
            results["created"].append({"path": path, "url": url})
            print(f"✅ Created: {path}")
        except Exception as e:
            results["errors"].append({"path": path, "error": str(e)})
            print(f"❌ Error creating {path}: {e}")
    
    return results


if __name__ == "__main__":
    print("🚀 Initializing React Native project in GitHub...")
    results = create_react_native_project()
    
    print(f"\n📊 Results:")
    print(f"  Created: {len(results['created'])} files")
    print(f"  Errors: {len(results['errors'])} files")
    
    if results['errors']:
        print("\n❌ Errors:")
        for error in results['errors']:
            print(f"  - {error['path']}: {error['error']}")
