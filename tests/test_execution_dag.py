import pytest
from runtime.dag.execution_graph import ExecutionDAG, DAGNode


@pytest.mark.asyncio
async def test_execution_dag_parallel():
    node1 = DAGNode(id="n1", action="fetch_data")
    node2 = DAGNode(id="n2", action="process_data", depends_on=["n1"])

    dag = ExecutionDAG([node1, node2])

    executed = []
    async def executor(node):
        executed.append(node.id)
        return f"result_{node.id}"

    results = await dag.execute(executor)
    assert len(results) == 2
    assert executed == ["n1", "n2"]
    assert results["n1"] == "result_n1"
    assert results["n2"] == "result_n2"
