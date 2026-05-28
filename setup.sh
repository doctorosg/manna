#!/bin/bash
echo "🍞 Setting up Manna Bible Trivia..."

# Check for xcodegen
if ! command -v xcodegen &> /dev/null; then
    echo "Installing XcodeGen..."
    brew install xcodegen
fi

# Generate Xcode project
xcodegen generate
echo "✅ Manna.xcodeproj generated"

# Open in Xcode
open Manna.xcodeproj
echo "🚀 Opening in Xcode..."
