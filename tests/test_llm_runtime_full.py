import pytest
from runtime.ai_runtime import AIRuntime
from runtime.llm.contracts import ExecutionContext, ProviderProfile


@pytest.mark.asyncio
async def test_ai_runtime_full_initialization():
    ai_runtime = AIRuntime()
    await ai_runtime.start()

    # Check default profiles
    profiles = ai_runtime.llm.providers.list_profiles()
    assert len(profiles) >= 3

    # Check default profile
    default_prof = ai_runtime.llm.providers.get_profile()
    assert default_prof is not None
    assert default_prof.is_default is True

    # Test adding new local vLLM provider profile
    vllm_profile = ProviderProfile(
        id="vllm-local",
        name="Local vLLM Cluster",
        provider_type="openai",
        base_url="http://localhost:8000/v1",
        default_model="vllm-model"
    )
    ai_runtime.llm.providers.add_profile(vllm_profile)

    client = ai_runtime.llm.providers.get_client("vllm-local")
    assert client is not None
    assert client.profile.name == "Local vLLM Cluster"

    # Test health monitor check
    health_res = await ai_runtime.health.check_provider_health("vllm-local")
    assert "status" in health_res

    await ai_runtime.shutdown()
