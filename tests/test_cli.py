"""Integration tests for the CLI."""

from click.testing import CliRunner

from ts_name.cli import main


class TestCLI:
    """Tests for the command-line interface."""

    def test_cli_requires_cookie_search(self) -> None:
        """Test that search command requires a cookie."""
        runner = CliRunner()
        result = runner.invoke(main, ["search", "--help"])
        assert result.exit_code == 0
        assert "cookie" in result.output.lower() or "--cookie" in result.output

    def test_cli_help(self) -> None:
        """Test that help output works."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "search" in result.output.lower()
        assert "set-name" in result.output.lower()

    def test_cli_search_help(self) -> None:
        """Test that search subcommand help works."""
        runner = CliRunner()
        result = runner.invoke(main, ["search", "--help"])
        assert result.exit_code == 0
        assert "cookie" in result.output.lower()
        assert "words" in result.output.lower()

    def test_cli_search_word_option(self) -> None:
        """Test that word option is available in search."""
        runner = CliRunner()
        result = runner.invoke(main, ["search", "--help"])
        assert "-w" in result.output or "--words" in result.output

    def test_cli_search_length_options(self) -> None:
        """Test that length options are available in search."""
        runner = CliRunner()
        result = runner.invoke(main, ["search", "--help"])
        assert "-m" in result.output or "--max-length" in result.output
        assert "--min-length" in result.output

    def test_cli_search_operator_option(self) -> None:
        """Test that operator option is available in search."""
        runner = CliRunner()
        result = runner.invoke(main, ["search", "--help"])
        assert "-o" in result.output or "--operator" in result.output
        assert "and" in result.output.lower()
        assert "or" in result.output.lower()

    def test_cli_search_limit_option(self) -> None:
        """Test that limit option is available in search."""
        runner = CliRunner()
        result = runner.invoke(main, ["search", "--help"])
        assert "-l" in result.output or "--limit" in result.output

    def test_cli_search_examples_in_help(self) -> None:
        """Test that search help contains usage examples."""
        runner = CliRunner()
        result = runner.invoke(main, ["search", "--help"])
        assert "Examples:" in result.output or "examples" in result.output.lower()

    def test_cli_set_name_help(self) -> None:
        """Test that set-name subcommand help works."""
        runner = CliRunner()
        result = runner.invoke(main, ["set-name", "--help"])
        assert result.exit_code == 0
        assert "cookie" in result.output.lower()
        assert "name" in result.output.lower() or "NAME" in result.output

    def test_cli_set_name_examples(self) -> None:
        """Test that set-name help contains examples."""
        runner = CliRunner()
        result = runner.invoke(main, ["set-name", "--help"])
        assert "Examples:" in result.output or "examples" in result.output.lower()
