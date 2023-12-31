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
        assert logos_output == '#line 1 "Tweak.x"'

    def test_config_name_invalid__unknown_generator(self) -> None:
        # Given a source file that sets the generator to something unknown/unsupported
        test_case = """

        %config(generator=foobar)

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
            "Could not find or check module 'Logos::Generator::foobar::Generator' [THIS MAY BE A PROBLEM!] at bin/lib/Logos/Generator.pm"
            in error_lines[0]
        )
        assert "Tweak.x: error: I can't find the 'foobar' Generator!" in error_lines[1]

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

        # And the produced error output should contain the expected values
        error_lines = stderr.splitlines()
        assert len(error_lines) == 1
        assert "Tweak.x: error: I can't find the 'Internal' Generator, did you mean 'internal'?" in error_lines[0]
