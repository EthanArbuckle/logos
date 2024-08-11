import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple


class LogosExecutor:
    @classmethod
    def logos_path(cls) -> Path:
        return Path(__file__).parent.parent / "bin" / "logos.pl"

    @classmethod
    def _sanitize_logos_output_for_unit_tests(cls, dirty_output: str | None, source_file_path: Path) -> str | None:
        if dirty_output is None or len(dirty_output) == 0:
            return None
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
        clean_output = clean_output.replace(containing_path_str, "").strip()

        # Remove line numbers from the output
        reconstructed_output = ""
        for line in clean_output.splitlines():
            words = line.split()
            for idx, word in enumerate(words):
                if "line" in word and idx + 1 < len(words) and words[idx + 1].strip().replace(".", "").isdigit():
                    has_period = words[idx + 1].endswith(".")
                    words[idx + 1] = "{num}"
                    if has_period:
                        words[idx + 1] += "."
                    continue

            reconstructed_output += " ".join(words) + "\n"
        return reconstructed_output.strip()

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

            logos_cmd_args = [
                LogosExecutor.logos_path().as_posix(),
                source_file_path.as_posix(),
            ]

            logos_proc = subprocess.run(logos_cmd_args, text=True, capture_output=True)
            stdout = None
            if logos_proc.returncode == 0 and len(logos_proc.stderr) == 0:
                stdout = LogosExecutor._sanitize_logos_output_for_unit_tests(logos_proc.stdout, source_file_path)
            stderr = LogosExecutor._sanitize_logos_output_for_unit_tests(logos_proc.stderr, source_file_path)

            return stdout, stderr
