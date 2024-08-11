import platform

from logos_executor import LogosExecutor


class TestLogosGeneratorConfigName:
    def test_config_name_valid(self) -> None:
        # Given a source file that sets the generator to a valid name
        test_case = """

        %config(generator=internal)

        """

        # When the source file is preprocessed
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)

        # Then the preprocessing should complete successfully
        assert logos_output is not None
        assert stderr is None

        # And the produced output should contain the expected value
        assert logos_output == '#line {num} "Tweak.x"'

    def test_config_name_invalid__unknown_generator(self) -> None:
        # Given a source file that sets the generator to something unknown/unsupported
        test_case = """

        %config(generator=fakeGenerator)

        """

        # When the source file is preprocessed
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)

        # Then the preprocessing should fail
        assert stderr is not None
        assert logos_output is None

        # And the produced error output should contain the expected values
        error_lines = stderr.splitlines()
        assert len(error_lines) == 2
        assert (
            "Could not find or check module 'Logos::Generator::fakeGenerator::Generator' [THIS MAY BE A PROBLEM!] at bin/lib/Logos/Generator.pm"
            in error_lines[0]
        )
        assert "Tweak.x: error: I can't find the fakeGenerator Generator!" in error_lines[1]

    def test_config_name_invalid__bad_capitalization(self) -> None:
        # Given a source file that uses a known generator but with incorrect capitalization
        test_case = """

        %config(generator=Internal)

        """

        # When the source file is preprocessed
        logos_output, stderr = LogosExecutor.preprocess_source(test_case)

        # Then the preprocessing should fail
        assert stderr is not None
        assert logos_output is None

        # And the produced error output should contain the expected values.
        # This case gives me a different error when running on macOS
        error_lines = stderr.splitlines()
        if platform.system() == "Darwin":
            assert error_lines == [
                "Method 'findPreamble' does not exist on package Logos::Generator::Internal::Generator at bin/lib/Logos/Generator/Thunk.pm line {num}."
            ]
        else:
            assert error_lines == [
                "Could not find or check module 'Logos::Generator::Internal::Generator' [THIS MAY BE A PROBLEM!] at bin/lib/Logos/Generator.pm line {num}.",
                "Tweak.x: error: I can't find the Internal Generator!",
            ]
