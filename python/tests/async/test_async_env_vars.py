from e2b_code_interpreter.code_interpreter_async import AsyncSandbox


async def test_env_vars_sandbox():
    sbx = await AsyncSandbox.create(envs={"FOO": "bar"})
    result = await sbx.notebook.exec_cell("import os; os.getenv('FOO')")
    assert result.text == "bar"
    await sbx.kill()


async def test_env_vars_in_exec_cell(async_sandbox: AsyncSandbox):
    result = await async_sandbox.notebook.exec_cell(
        "import os; os.getenv('FOO')", envs={"FOO": "bar"}
    )
    assert result.text == "bar"


async def test_env_vars_override(debug: bool):
    sbx = await AsyncSandbox.create(envs={"FOO": "bar", "SBX": "value"})
    await sbx.notebook.exec_cell(
        "import os; os.environ['FOO'] = 'bar'; os.environ['RUNTIME_ENV'] = 'async_python_runtime'"
    )
    result = await sbx.notebook.exec_cell(
        "import os; os.getenv('FOO')", envs={"FOO": "baz"}
    )
    assert result.text == "baz"

    # This can fail if running in debug mode (there's a race condition with the restart kernel test)
    result = await sbx.notebook.exec_cell("import os; os.getenv('RUNTIME_ENV')")
    assert result.text == "async_python_runtime"

    if not debug:
        result = await sbx.notebook.exec_cell("import os; os.getenv('SBX')")
        assert result.text == "value"

    # This can fail if running in debug mode (there's a race condition with the restart kernel test)
    result = await sbx.notebook.exec_cell("import os; os.getenv('FOO')")
    assert result.text == "bar"

    await sbx.kill()
