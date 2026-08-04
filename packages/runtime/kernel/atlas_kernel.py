"""
Atlas Runtime Kernel — Refactored as AI Operating System

Architecture:
- Runtime is the OS (schedules, executes, verifies, recovers)
- LLM is only a planning engine (intent, difficulty, decomposition)
- Two local models: Planner LLM + Embedding Model (via Ollama)
- Cloud LLM only for: complex reasoning, large context, code review
"""
import asyncio
import logging
from typing import Optional

from runtime.events.bus import EventBus
from runtime.kernel.state_manager import StateManager
from runtime.kernel.task_manager import TaskManager
from runtime.context.builder import ContextBuilder
from planner.local_planner import LocalPlanner
from execution.scheduler import ExecutionScheduler
from runtime.kernel.aggregator import ResultAggregator
from runtime.capabilities.registry import CapabilityRegistry
from runtime.policy.policy import PolicyEngine
from runtime.kernel.openrouter import OpenRouterClient

from runtime.kernel.rollback import RollbackEngine
from runtime.artifacts.manager import ArtifactsManager
from runtime.kernel.history import HistoryManager
from runtime.kernel.verifier import VerificationEngine
from runtime.kernel.response_generator import ResponseGenerator
from runtime.intelligence.memory import MemoryEngine
from runtime.intelligence.local_llm import LocalLLMManager
from runtime.intelligence.intent import IntentDetector
from runtime.intelligence.llm_router import LLMRouter
from runtime.session.conversation import ConversationManager, SessionManager
from plugins.manager import PluginManager

logger = logging.getLogger("atlas.kernel")


class AtlasKernel:
    def __init__(self):
        # ── Event Bus (first — everything subscribes to this) ──────────────
        self.bus = EventBus()

        # ── State & Session ────────────────────────────────────────────────
        self.state = StateManager()
        self.tasks = TaskManager(self.state, self.bus)
        self.conversations = ConversationManager()
        self.sessions = SessionManager(self.conversations)

        # ── Intelligence Layer ─────────────────────────────────────────────
        self.memory = MemoryEngine()
        self.local_llm = LocalLLMManager(bus=self.bus)  # Ollama auto-detect

        # ── Unified AI Platform & LLM Runtime ─────────────────────────────
        from runtime.ai_runtime import AIRuntime
        self.ai_runtime = AIRuntime(memory_engine=self.memory)

        # ── Cloud LLM (compatibility wrapper) ────────────────────────────
        self.openrouter = OpenRouterClient()

        # ── Routers & Classifiers ─────────────────────────────────────────
        self.intent_detector = IntentDetector(
            local_llm=self.local_llm,
            openrouter=self.openrouter
        )
        self.llm_router = LLMRouter(
            local_llm=self.local_llm,
            openrouter=self.openrouter
        )

        # ── Context ────────────────────────────────────────────────────────
        self.context = ContextBuilder(self.state, self.memory)

        # ── Execution Engine ───────────────────────────────────────────────
        self.policy = PolicyEngine()
        self.rollback = RollbackEngine()
        self.verifier = VerificationEngine()
        self.artifacts = ArtifactsManager()
        self.history = HistoryManager()

        # ── Capability Registry & Plugins ─────────────────────────────────
        self.registry = CapabilityRegistry(self.state, self.memory)
        self.plugins = PluginManager(self.registry)
        self.plugins.auto_load_plugins()

        # ── Planner (LLM-based graph decomposition) ────────────────────────
        self.planner = LocalPlanner(self.openrouter)
        self.scheduler = ExecutionScheduler(self.registry, self.bus, self.policy, self.rollback)

        # ── Aggregator (legacy) ────────────────────────────────────────────
        self.aggregator = ResultAggregator(self.openrouter, self.bus)

    async def start(self):
        """Boot sequence: start EventBus, then initialize Local LLM and AIRuntime."""
        await self.bus.start()
        await self.ai_runtime.start()

        # Initialize Local LLM asynchronously — does not block boot
        asyncio.create_task(self._boot_local_llm())

    async def _boot_local_llm(self):
        """API LLM Mode Active — local LLM is disabled as requested."""
        logger.info("ATLAS ENGINE: API LLM Mode active (Cloud API Models strictly enabled).")

    def stop(self):
        self.bus.stop()

    async def execute_goal(self, goal: str, exec_id: str, conversation_id: Optional[str] = None):
        import time
        start_time = time.time()
        logger.info(f"[{exec_id}] STARTING GOAL EXECUTION: {goal!r}")

        # ── Session & Conversation ─────────────────────────────────────────
        conv_id = conversation_id or exec_id
        self.conversations.add_user_message(conv_id, goal)
        conv_context = self.conversations.get_context(conv_id, limit=6)

        # ── 1. Create Task ─────────────────────────────────────────────────
        task = await self.tasks.create_task(goal, conv_id, task_id=exec_id)
        task.results = []

        try:
            # ── 2. Intent Detection ─────────────────────────────────────────
            t0 = time.time()
            await self.bus.publish("THOUGHT", {
                "task_id": exec_id, "content": "Detecting intent..."
            })
            intent_result = self.intent_detector.detect(goal, conv_context)
            task.intent = intent_result
            intent_duration_ms = round((time.time() - t0) * 1000, 2)

            logger.info(
                f"[{exec_id}] INTENT DETECTED [{intent_duration_ms}ms]: "
                f"intent={intent_result['intent']!r} | difficulty={intent_result['difficulty']} | "
                f"needs_cloud={intent_result['needs_cloud']}"
            )

            await self.bus.publish("THOUGHT", {
                "task_id": exec_id,
                "content": (
                    f"Intent: {intent_result['intent']} [{intent_duration_ms}ms] | "
                    f"Difficulty: {intent_result['difficulty']} | "
                    f"Cloud: {intent_result['needs_cloud']}"
                )
            })

            # ── 3. Direct Answer shortcut ──────────────────────────────────
            if intent_result.get("direct_answer") and intent_result["difficulty"] == "easy":
                answer = intent_result["direct_answer"]
                self.conversations.add_assistant_message(conv_id, answer)
                await self.bus.publish("message", {"task_id": exec_id, "content": answer})
                await self.tasks.mark_done(exec_id)
                total_duration_ms = round((time.time() - start_time) * 1000, 2)
                logger.info(f"[{exec_id}] DIRECT ANSWER COMPLETED [{total_duration_ms}ms]")
                await self.bus.publish("finish", {
                    "task_id": exec_id,
                    "result": {"status": "completed", "artifacts": [], "conversation_id": conv_id}
                })
                return

            # ── 4. Route to correct LLM ────────────────────────────────────
            reasoning_session = self.llm_router.route(intent_result)

            # ── 5. Build Context Payload ───────────────────────────────────
            t1 = time.time()
            await self.bus.publish("THOUGHT", {
                "task_id": exec_id, "content": "Building context snapshot..."
            })
            caps_manifest = self.registry.get_capabilities_manifest()

            semantic_memories = self.memory.search_similar(goal, top_k=3)
            task.semantic_context = semantic_memories

            ctx_payload = self.context.build_context(task, caps_manifest)
            ctx_duration_ms = round((time.time() - t1) * 1000, 2)
            logger.info(f"[{exec_id}] CONTEXT SNAPSHOT BUILT [{ctx_duration_ms}ms] ({len(ctx_payload)} chars)")

            # ── 6. Plan Generation ─────────────────────────────────────────
            t2 = time.time()
            await self.bus.publish("THOUGHT", {
                "task_id": exec_id, "content": "Planning execution graph..."
            })
            intent_str, graph, needs_cloud = self.planner.generate_plan(ctx_payload)

            task.graph = graph
            task.needs_cloud_reasoning = needs_cloud or intent_result.get("needs_cloud", False)

            plan_duration_ms = round((time.time() - t2) * 1000, 2)
            ui_tasks = [f"{node.action}: {node.id}" for node in graph] if graph else []
            logger.info(f"[{exec_id}] PLAN GENERATED [{plan_duration_ms}ms]: {len(graph)} nodes — {ui_tasks}")

            await self.bus.publish("plan", {"task_id": exec_id, "tasks": ui_tasks})
            await self.bus.publish("THOUGHT", {
                "task_id": exec_id,
                "content": f"Plan: {len(graph)} step(s) [{plan_duration_ms}ms] — {', '.join(ui_tasks)}"
            })

            if not graph:
                logger.warning(f"[{exec_id}] Empty plan graph generated. Falling back to direct LLM call.")
                response = reasoning_session.call(
                    [{"role": "user", "content": goal}],
                    system="You are Atlas. Answer the user's question concisely."
                )
                self.conversations.add_assistant_message(conv_id, response)
                await self.bus.publish("message", {"task_id": exec_id, "content": response})
                await self.tasks.mark_done(exec_id)
                await self.bus.publish("finish", {
                    "task_id": exec_id,
                    "result": {"status": "completed", "artifacts": [], "conversation_id": conv_id}
                })
                return

            # ── 7. Execute Graph Nodes ─────────────────────────────────────
            t3 = time.time()
            logger.info(f"[{exec_id}] EXECUTING GRAPH NODES ({len(graph)} steps)...")
            await self.scheduler.execute_graph(task)

            exec_duration_ms = round((time.time() - t3) * 1000, 2)
            logger.info(f"[{exec_id}] GRAPH EXECUTION COMPLETED [{exec_duration_ms}ms]")

            task.results = [
                node.result for node in task.graph if hasattr(node, 'result') and node.result
            ]

            # ── 8. Verify Steps (Deterministic — no LLM) ──────────────────
            await self.bus.publish("THOUGHT", {
                "task_id": exec_id, "content": "Verifying execution..."
            })
            for node in task.graph:
                if hasattr(node, 'result') and node.result:
                    v_result = self.verifier.verify(
                        node.action, node.parameters.get("action", ""), node.parameters, node.result
                    )
                    if not v_result.success:
                        logger.warning(f"Verification failed for {node.id}: {v_result.reason}")
                        await self.bus.publish("THOUGHT", {
                            "task_id": exec_id,
                            "content": f"⚠️ Verification issue: {v_result.reason}"
                        })

            # ── 9. Generate Response ───────────────────────────────────────
            await self.bus.publish("THOUGHT", {
                "task_id": exec_id, "content": "Generating response..."
            })
            response_gen = ResponseGenerator(reasoning_session=reasoning_session)
            final_response = response_gen.generate(task, intent_result)

            # Fallback to aggregator for complex multi-step results
            if not final_response or len(final_response) < 10:
                final_response = await self.aggregator.summarize(task)

            # ── 10. Save Artifact if Large ─────────────────────────────────
            if len(final_response) > 500 or "```" in final_response:
                art_path = self.artifacts.save_artifact(exec_id, final_response, "md")
                if art_path:
                    task.artifacts.append(art_path)

            # ── 11. Store Response in Conversation & History ───────────────
            self.conversations.add_assistant_message(conv_id, final_response, task.artifacts)
            self.history.record_task(task)

            # Store semantically useful observations in memory
            if len(final_response) > 50:
                self.memory.store_semantic(
                    f"Goal: {goal}\nResult: {final_response[:300]}",
                    metadata={"exec_id": exec_id, "intent": intent_result.get("intent")}
                )

            # ── 12. Publish & Finish ───────────────────────────────────────
            await self.bus.publish("message", {"task_id": exec_id, "content": final_response})
            await self.tasks.mark_done(exec_id, task.artifacts)
            await self.bus.publish("finish", {
                "task_id": exec_id,
                "result": {
                    "status": "completed",
                    "artifacts": task.artifacts,
                    "conversation_id": conv_id
                }
            })

        except Exception as e:
            logger.error(f"Execution failed [{exec_id}]: {e}", exc_info=True)
            await self.tasks.mark_failed(exec_id, str(e))
            await self.bus.publish("error", {"task_id": exec_id, "error": str(e)})
