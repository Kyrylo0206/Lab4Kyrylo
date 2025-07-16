# Lab 4

The **goal** of this lab is to figure out how to help AIs use our APIs
U can use [OpenAI playground](https://platform.openai.com/playground) to experiment

## Task 1: Function calling (6)

1. Read through prompting guide for [non-reasoning](https://cookbook.openai.com/examples/gpt4-1_prompting_guide) and [reasoning](https://platform.openai.com/docs/guides/reasoning-best-practices) models
2. Review function calling guides from:
   1. [OpenAI](https://platform.openai.com/docs/guides/function-calling?api-mode=chat)
   2. [Huggingface](https://huggingface.co/docs/hugs/guides/function-calling)
   3. [Google](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling)
3. Check examples in [this repo](/function-calling-client/)
4. Allow LLM to use your rest client developed in CA-1 (like in example above) (3 points)
   1. Level 1: Add guardrails on token expedinture (1 point)
   2. Level 2: Add multiple tools. Invent prompt which requires chaining them (e.g. 'Update note created by user ihor@pm.me, to 'send your CA-2'. if it is not present - create it')
   3. Level 3: Add quardrail agins prompt injection (1 point)

## Task 2 Model Context Protocol (9)

1. Read about MCPs
   1. [Nice deeplearning.ai course](https://learn.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic)
   2. [Official doc](https://modelcontextprotocol.io/introduction)
   3. [Dou article](https://dou.ua/forums/topic/53550/)
2. Check examples in [this repo](/server/mcp_server.py) and [this nice crash course](https://github.com/daveebbelaar/ai-cookbook/blob/main/mcp/crash-course/2-understanding-mcp/README.md)
3. Advertise capabilities of your restful API from lab1 as MCP server. Do not forget about guardrails. (9 points)
   - Pro tip - use [inspector](https://modelcontextprotocol.io/docs/tools/inspector) to verify your work

## Task 3 A2A (3 extra bonus points counting towards 112%)

1. Read about A2A
   1. [official](https://a2aprotocol.ai/)
   2. [dev.to](https://dev.to/czmilo/a2a-protocol-development-guide-1f49)
2. Pack producer from lab2 as AI agent. Expose it's skills to produce via a2a. (1 point)
3. Pack consumer from lab2 as AI agent. Integrate it with producer refer to this [example](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/airbnb_planner_multiagent) or this [one](https://medium.com/ai-cloud-lab/building-multi-agent-ai-app-with-googles-a2a-agent2agent-protocol-adk-and-mcp-a-deep-a94de2237200)
