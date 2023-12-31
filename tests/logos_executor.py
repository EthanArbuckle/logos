import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple


class LogosExecutor:
    @classmethod
    def logos_path(cls) -> Path:
        return Path(__file__).parent.parent / "bin" / "logos.pl"

    @classmethod
    def _sanitize_logos_output_for_unit_tests(cls, dirty_output: str, source_file_path: Path) -> str:
        # The output will contain references to the tempdir containing the source file.
        # To make testing/validating the output easier, remove the references
        #   before: #line 1 "/var/folders/f1/t2nfrnvd2sb98lm72jp348s00000gn/T/tmp931oxgn1/source-file.x"
        #    after: #line 1 "source-file.x"
        # Include a trailing slash
        temp_dir_path_str = f"{source_file_path.parent.as_posix()}/"
        clean_output = dirty_output.replace(temp_dir_path_str, "")

        # Also remove file references that contain the full path to logos files
        # Example: PROBLEM! at /some/user/theos/vendor/logos/bin/lib/Logos/Generator.pm line 43
        containing_path = LogosExecutor.logos_path().parent.parent
        containing_path_str = f"{containing_path.as_posix()}/"
        clean_output = clean_output.replace(containing_path_str, "")

        # Strip excessive newlines
        #   before: `#line 1 "source-file.x"\n\n\n        \n\n        \n`
        #    after: `#line 1 "source-file.x`
        clean_output = clean_output.strip()
        return clean_output

    @classmethod
    def preprocess_source(
        cls, source_code: str, source_file_extension: str = ".x"
    ) -> Tuple[Optional[str], Optional[str]]:
        """Run the given source code through logos.
        returns stdout, stderr
        """
        with tempfile.TemporaryDirectory() as tempdir:
            if "." not in source_file_extension:
                source_file_extension = f".{source_file_extension}"

            source_file_path = Path(tempdir) / f"Tweak{source_file_extension}"
            source_file_path.write_text(source_code)

            try:
                logos_cmd_args = [
                    LogosExecutor.logos_path(),
                    source_file_path.as_posix(),
                ]

                logos_output = subprocess.check_output(logos_cmd_args, text=True, stderr=subprocess.STDOUT)
                sanitized_output = LogosExecutor._sanitize_logos_output_for_unit_tests(logos_output, source_file_path)
                return sanitized_output, None

            except subprocess.CalledProcessError as subproc_exc:
                return None, LogosExecutor._sanitize_logos_output_for_unit_tests(subproc_exc.stdout, source_file_path)
