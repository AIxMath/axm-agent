# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-XX

### Added
- Initial release of AXM Agent
- Core Agent class with decorator-based tool registration
- Support for OpenAI (GPT-4, GPT-3.5) and Anthropic (Claude) LLMs
- MCP (Model Context Protocol) server support
- Function calling with automatic type validation
- PlanningAgent for task decomposition and execution
- MultiAgent system for agent collaboration
- Structured output with Pydantic models
- Async and streaming support
- Conversation memory management
- Comprehensive documentation and examples
- Test suite with pytest
- CI/CD with GitHub Actions

### Features
- 🎯 Simple decorator API for defining tools
- 🔌 Full MCP integration
- 📞 Automatic function calling
- 📋 Built-in task planning
- ✅ Format-constrained output (JSON, Pydantic)
- ⚡ Async & streaming support
- 🎨 Multi-agent collaboration
- 🔄 Memory & context management
- 🛠️ Multiple LLM provider support

[0.1.0]: https://github.com/yourusername/axm-agent/releases/tag/v0.1.0
