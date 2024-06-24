from unittest.mock import Mock

from lib.chains.git.chain import GitChain


def test_get_tool_output():
    llm_mock = Mock()
    ai_msg_mock = Mock()
    ai_msg_mock.tool_calls = [
        {"name": "test_tool_1", "args": "test_args_1"},
        {"name": "test_tool_2", "args": "test_args_2"},
    ]
    tools_mock = {
        "test_tool_1": Mock(),
        "test_tool_2": Mock(),
    }
    tools_mock["test_tool_1"].invoke.return_value = "Test tool output 1"
    tools_mock["test_tool_2"].invoke.return_value = "Test tool output 2"
    git_chain = GitChain(llm_mock, tools_mock)

    status = git_chain._get_tool_output(ai_msg_mock)

    tools_mock["test_tool_1"].invoke.assert_called_once_with("test_args_1")
    tools_mock["test_tool_2"].invoke.assert_called_once_with("test_args_2")
    assert status == "Test tool output 2"


def test_get_tool_output2():
    llm_mock = Mock()
    ai_msg_mock = Mock()
    ai_msg_mock.tool_calls = [{"name": "test_tool", "args": "test_args"}]
    tools_mock = {"test_tool": Mock()}
    tools_mock["test_tool"].invoke.return_value = "Test tool output"
    git_chain = GitChain(llm_mock, tools_mock)

    status = git_chain._get_tool_output(ai_msg_mock)

    tools_mock["test_tool"].invoke.assert_called_once_with("test_args")
    assert status == "Test tool output"
